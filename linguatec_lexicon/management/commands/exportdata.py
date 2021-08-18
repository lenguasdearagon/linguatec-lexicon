from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon import utils
from linguatec_lexicon.models import (
    Entry, Example, Lexicon, VerbalConjugation, Word)

import csv
import os.path


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon code where data will be exported from",
        )
        parser.add_argument(
            'output_file', type=str,
            help='Name of file where data will be written to. (must be a csv file)'
        )

    def handle(self, *args, **options):
        self.lexicon_code = options['lexicon_code']
        self.output_file = options['output_file']
        # check that a lexicon with that code exist
        try:
            src, dst = utils.get_lexicon_languages_from_code(self.lexicon_code)
            self.lexicon = Lexicon.objects.get(src_language=src, dst_language=dst)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        # check if csv file already exists
        if os.path.isfile(self.output_file):
            raise CommandError('Error: A csv with that name already exists: ' + self.output_file)

        self.write_to_csv_file()

    def write_to_csv_file(self):

        word_list = list(Word.objects.filter(lexicon=self.lexicon).order_by('term'))

        with open(self.output_file, 'w') as outfile:

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
