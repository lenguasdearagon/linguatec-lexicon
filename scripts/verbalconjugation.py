import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynesite.settings')
django.setup()

from linguatec_lexicon.models import Entry, VerbalConjugation


def main():
    entries = Entry.words_conjugation()

    for k_entry, v_raw in entries.items():
        for entry in Entry.objects.filter(word__term=k_entry):
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


if __name__ == '__main__':
    """
    Setup:
    =====
    For run this test, you need to move it in the root directory of the project
    and change mysite for the correct name of the project
    """

    main()
