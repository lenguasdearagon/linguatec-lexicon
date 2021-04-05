from django.core.management.base import BaseCommand

from linguatec_lexicon.models import Entry, VerbalConjugation


class Command(BaseCommand):

    def handle(self, *args, **options):
        for k_entry, v_raw in Entry.words_conjugation().items():
            for entry in Entry.objects.filter(word__term=k_entry, word__lexicon__src_language='es'):
                verbs = VerbalConjugation.objects.filter(entry=entry)
                if verbs:
                    verb = verbs.first()
                    verb.raw_verbs = v_raw
                    verb.save()
                else:
                    VerbalConjugation.objects.create(
                        entry=entry,
                        raw_verbs=v_raw
                    )
