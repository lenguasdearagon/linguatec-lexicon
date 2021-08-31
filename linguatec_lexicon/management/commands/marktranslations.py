import re
from django.core.exceptions import ValidationError

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.functional import cached_property

from linguatec_lexicon.models import Entry, Lexicon
from linguatec_lexicon.validators import validate_balanced_parenthesis


class Command(BaseCommand):
    help = 'Fill marked_translation field to link words'
    default_batch_size = 100
    # words including dash '-' and slash '/' not surrounded by parenthesis '()'
    regex = r'(?<!\()\b\S+\b(?![\w\s]*[\)])'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size', type=int,
            help=("Controls how many entries are updated in a single query "
                  "Directly passed to bulk_update. By default: {}").format(self.default_batch_size),
        )

    def handle(self, *args, **options):
        self.batch_size = options['batch_size'] or self.default_batch_size

        for lexicon in Lexicon.objects.all():
            # cache lexicon words on a set (hash lookup has better performance)
            # TODO(@slamora): handle if there is not reverse pair
            lex_reverse = lexicon.get_reverse_pair()
            self.lex_words = self.retrieve_lexicon_words(lex_reverse)
            updated, total = self.fill_marked_translation(lexicon)
            self.stdout.write("Lexicon {} marked {} of {} entries".format(lexicon.code, updated, total))

    def retrieve_lexicon_words(self, lexicon):
        return {word[0]: word[1] for word in lexicon.words.values_list('term', 'id')}

    @transaction.atomic
    def fill_marked_translation(self, lexicon):
        entries = []
        qs = Entry.objects.filter(word__lexicon=lexicon)
        for entry in qs:
            try:
                marked_translation = self.mark_text(entry.translation)
            except ValidationError:
                variation_name = entry.variation.name if entry.variation else ''
                msg = "[{}@{}] '{}' Unbalanced parenthesis on entry '{}'".format(
                    lexicon.code, variation_name, entry.word.term, entry.translation)
                self.stdout.write(self.style.ERROR(msg))
            if "</trans>" in marked_translation:
                entry.marked_translation = marked_translation
                entries.append(entry)

        Entry.objects.bulk_update(entries, ['marked_translation'], batch_size=self.batch_size)

        return len(entries), qs.count()

    def mark_text(self, text):
        text_marked = ''
        for chunk in split_by_parenthesis(text):
            if not chunk.startswith('('):
                chunk = re.sub(self.regex, self.mark_word, chunk)
            text_marked += chunk

        return text_marked

    def mark_word(self, matchobj):
        match_chunk = matchobj.group(0)
        try:
            word_id = self.lex_words[match_chunk]
        except KeyError:
            return match_chunk
        return "<trans word={}>{}</trans>".format(word_id, match_chunk)


def split_by_parenthesis(text):
    validate_balanced_parenthesis(text)
    groups = []
    start = 0
    while True:
        end = text.find('(', start)
        if end >= 0:
            chunk = text[start:end]
            if chunk:
                groups.append(chunk)
                start = end

            # find closing parenthesis
            end = text.find(')', end) + 1
            groups.append(text[start:end])
            start = end

        else:
            chunk = text[start:]
            if chunk:
                groups.append(chunk)
            break

    return groups
