import re

from django.core.management.base import BaseCommand
from django.db import transaction
from linguatec_lexicon.models import Entry, Lexicon, Word


class Command(BaseCommand):
    help = 'Fill marked_translation field to link words'

    def handle(self, *args, **options):
        for lexicon in Lexicon.objects.all():
            updated, total = self.fill_marked_translation(lexicon)
            self.stdout.write("Lexicon {} marked {} of {} entries".format(lexicon.code, updated, total))

    @transaction.atomic
    def fill_marked_translation(self, lexicon):
        self.lex = lexicon
        # TODO(@slamora): handle if there is not reverse pair
        self.lex_reverse = lexicon.get_reverse_pair()
        entries = []

        qs = Entry.objects.filter(word__lexicon=lexicon)
        for entry in qs:
            marked_translation = re.sub(r'(\b\S+\b)', self.mark_word, entry.translation)
            if "</trans>" in marked_translation:
                entry.marked_translation = marked_translation
                entries.append(entry)

        Entry.objects.bulk_update(entries, ['marked_translation'])

        return len(entries), qs.count()

    def mark_word(self, matchobj):
        match_chunk = matchobj.group(1)
        translation_exists = Word.objects.filter(lexicon=self.lex_reverse, term=match_chunk).exists()
        if translation_exists:
            return "<trans lex=" + self.lex_reverse.code + ">" + match_chunk + "</trans>"
        return match_chunk
