import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynesite.settings')
django.setup()

from linguatec_lexicon.models import Entry


def main():
    entries = Entry.words_conjugation()

    with open("conjugation.csv", 'w') as infile:
        infile.write("Verbo en castellano; Verbos en Aragones\n")
        for castilian, arag in entries.items():
            aragonese = ", ".join(arag)
            infile.write(f"{castilian}; {aragonese}\n")


if __name__ == '__main__':
    """
    Setup:
    =====
    For run this test, you need to move it in the root directory of the project
    and change mysite for the correct name of the project
    """

    main()
