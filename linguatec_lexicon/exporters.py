from linguatec_lexicon.models import (
    Entry, Word, VerbalConjugation, Example)

import csv

from django.http import HttpResponse


def write_to_csv_file_data(lexicon, output_file):
    def write_to_file(outfile):

        fieldnames = [
                'word',
                'gramcats',
                'translation',
                '(empty)',
                'example',
                'verbal conjugation',
            ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')

        for word in word_list:

            to_write = {'word': word.term}

            entry_list = Entry.objects.filter(word=word, variation=None)

            to_write['translation'] = ' // '.join(entry_list.values_list('translation', flat=True))

            to_write['gramcats'] = ' // '.join(entry_list.values_list('gramcats__abbreviation', flat=True)
                                               .distinct().order_by('gramcats__abbreviation'))

            to_write['example'] = ''
            to_write['verbal conjugation'] = ''
            number_of_examples = 0
            number_of_verbal_conjugation = 0

            for entry in entry_list:
                examples = ' ; '.join(Example.objects.filter(entry=entry)
                                      .values_list('phrase', flat=True))
                if examples != '':
                    number_of_examples += 1

                to_write['example'] += examples + '// '

                verbal_conjugations = ' ; '.join(VerbalConjugation.objects.filter(entry=entry)
                                                 .values_list('raw', flat=True))

                if verbal_conjugations != '':
                    number_of_verbal_conjugation += 1

                to_write['verbal conjugation'] += verbal_conjugations + '// '

            if number_of_examples == 0:
                to_write['example'] = ''
            else:
                while to_write['example'][-3:] == '// ':
                    to_write['example'] = to_write['example'][:-3]

            if number_of_verbal_conjugation == 0:
                to_write['verbal conjugation'] = ''
            else:
                while to_write['verbal conjugation'][-3:] == '// ':
                    to_write['verbal conjugation'] = to_write['verbal conjugation'][:-3]

            writer.writerow(to_write)

    word_list = list(Word.objects.filter(lexicon=lexicon).order_by('term'))

    if output_file:
        with open(output_file, 'w') as outfile:
            write_to_file(outfile)
    else:
        response = HttpResponse(content_type='text/plain')
        write_to_file(response)
        response['Content-Disposition'] = 'attachment; filename="data.csv"'
        return response


def write_to_csv_file_variation(lexicon_id, variation_id, output_file):
    def write_to_file(outfile):
        entry_list = Entry.objects.filter(variation=variation_id).values('word__term').distinct().order_by('word__term')

        fieldnames = [
                'word',
                'gramcats',
                'translation',
            ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')

        for entry in entry_list:
            try:
                word = Word.objects.get(term=entry['word__term'], lexicon=lexicon_id)
            except Word.DoesNotExist:
                continue

            to_write = {'word': word.term}

            to_write['gramcats'] = ' // '.join(Entry.objects.filter(word=word, variation=variation_id)
                                               .values_list('gramcats__abbreviation', flat=True)
                                               .distinct().order_by('gramcats__abbreviation'))

            to_write['translation'] = ' // '.join(Entry.objects.filter(word=word, variation=variation_id)
                                                  .values_list('translation', flat=True))

            writer.writerow(to_write)

    if output_file:
        with open(output_file, 'w') as outfile:
            write_to_file(outfile)
    else:
        response = HttpResponse(content_type='text/plain')
        write_to_file(response)
        response['Content-Disposition'] = 'attachment; filename="data.csv"'
        return response
