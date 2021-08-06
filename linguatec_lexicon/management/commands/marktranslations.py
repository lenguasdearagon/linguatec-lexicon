import re

from django.core.management.base import BaseCommand
from django.db import transaction
from linguatec_lexicon.models import Entry, Lexicon


class Command(BaseCommand):
    help = 'Fill marked_translation field to link words'
    default_batch_size = 100

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size', type=int,
            help=("Controls how many entries are updated in a single query "
                  "Directly passed to bulk_update. By default: {}").format(self.default_batch_size),
        )

    def handle(self, *args, **options):
        self.batch_size = options['batch_size'] or self.default_batch_size

        for lexicon in Lexicon.objects.all():
            updated, total = self.fill_marked_translation(lexicon)
            self.stdout.write("Lexicon {} marked {} of {} entries".format(lexicon.code, updated, total))

    @transaction.atomic
    def fill_marked_translation(self, lexicon):
        # TODO(@slamora): handle if there is not reverse pair
        self.lex_reverse = lexicon.get_reverse_pair()

        # cache lexicon words on a set (hash lookup has better performance)
        self.lex_words = set(self.lex_reverse.words.values_list('term', flat=True))

        entries = []
        qs = Entry.objects.filter(word__lexicon=lexicon)
        for entry in qs:
            marked_translation = re.sub(r'(\b\S+\b)', self.mark_word, entry.translation)
            if "</trans>" in marked_translation:
                entry.marked_translation = marked_translation
                entries.append(entry)

        Entry.objects.bulk_update(entries, ['marked_translation'], batch_size=self.batch_size)

        return len(entries), qs.count()

    def mark_word(self, matchobj):
        match_chunk = matchobj.group(1)
        translation_exists = match_chunk in self.lex_words
        if translation_exists:
            return "<trans lex=" + self.lex_reverse.code + ">" + match_chunk + "</trans>"
        return match_chunk
