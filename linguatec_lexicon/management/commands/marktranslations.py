import re

from django.core.management.base import BaseCommand
from django.db import transaction
from linguatec_lexicon.models import Entry, Word


class Command(BaseCommand):
    help = 'Fill marked_translation field to link words'

    def handle(self, *args, **options):
        self.fill_marked_translation()

    @transaction.atomic
    def fill_marked_translation(self):
        entries = []
        for entry in Entry.objects.filter(marked_translation=None):
            self.lex = entry.word.lexicon
            marked_translation = re.sub(r'(\b\S+\b)', self.mark_word, entry.translation)
            entry.marked_translation = marked_translation if "</trans>" in marked_translation else None
            if entry:
                entries.append(entry)

        Entry.objects.bulk_update(entries, ['marked_translation'])

    def mark_word(self, matchobj):
        translation_exists = Word.objects.filter(term=matchobj.group(1)).exclude(lexicon=self.lex).exists()
        if translation_exists:
            lex_code = self.lex.dst_language + '-' + self.lex.src_language
            return "<trans lex=" + lex_code + ">" + matchobj.group(1) + "</trans>"
        else:
            return matchobj.group(1)
