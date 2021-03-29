import string
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from linguatec_lexicon.models import Entry, Word, GramaticalCategory

gram_abb = GramaticalCategory.objects.filter(abbreviation__startswith='v.').values_list('abbreviation')

kind_of_verbs = {x[0] for x in gram_abb}

# get all entries that they are verbs, (17815)
entries = Entry.objects.filter(gramcats__abbreviation__in=kind_of_verbs).distinct()
# get all entries than the translation to be more than one word, (6792)
long_trans = [x for x in entries if len(x.translation.split(' ')) > 1]

# get all entries than the words_conjugation is equal to [], (87)
lost = []
for e in long_trans:
    if not e.words_conjugation():
        lost.append(e)


def main():
    if lost:
        alph = string.ascii_lowercase + 'ñáéíóú!-'
        without_entries = [] # 43 entries without correspondence in the oposite language
        problems_entries = [] # 44 problematic entries
        new_words = [] # 0 entries
        for e in lost:
            translation = ''
            for c in e.translation.lower():
               if c in alph:
                   translation += c
               else:
                   translation += ' '
            words = set(translation.split(' '))
            word_obj = Word.objects.filter(
                lexicon__src_language=e.word.lexicon.dst_language
            ).filter(
                lexicon__dst_language=e.word.lexicon.src_language
            ).filter(term__in=words)

            # filter only the verbs
            [x.gramcats() for x in word_obj]
            if not word_obj:
                without_entries.append(e)
            else:
                for x in word_obj:
                    for g in x.gramcats():
                        if g in kind_of_verbs:
                            new_words.append(x)
                    if not x in new_words:
                        problems_entries.append(x)
        # import pdb; pdb.set_trace()

        # cases:
            # 1
            # amanecer is translate as 'lusco, punto’l diya'
            # any of them is a verb in Aragonese

            # 2 there are cases with hyphenated compound words (-)
            # 3 hay casos con palabras que terminan con exclamacion !
            # 3 there are cases with words that end with exclamation (!)
            # resguardarse 'meter-se a retiro', 'meter-se' it has no entrance but yes 'meter'

            ## All cases of problems_entries:
            #
            # 'tal', 'allá', 'trabajo', 'la', 'menister', 'a', 'tierra', 'maitineta', 'material',
            # 'de', 'pobre', 'una', 'rápidamente', 'diya', 'menester', 'anuitardi', 'aquí',
            # 'mañanada', 'gorra', 'deprisa', 'punto', 'ropa', 'aliento', 'el', 'vaca', 'dicho',
            # 'tocar-las-se', 'retiro', 'tres', 'prisa', 'día', 'lusco', 'romana', 'piso',
            # 'para', 'tontamente', 'i', 'superior', 'dinero', 'tocar-se-las', 'pero', 'carne',
            # 'esbezar', 'estéril', 'grillar-se-las', 'maitinada', 'aldea', 'pausa', 'mañaneta',
            # 'sin', 'fruta', 'boca'

if __name__ == '__main__':
    """
    Setup:
    =====
    For run this test, you need to move it in the root directory of the project
    and change mysite for the correct name of the project

    Result:
    ======
    17815 entries as verbs
    6792 entries as verbs with a translation more long than one word
    87 lost
       43 without correspondence in the other language
       44 than it's not a verb or it's a composse word
    """
    main()
