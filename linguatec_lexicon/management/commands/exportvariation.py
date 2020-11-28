from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import (
    Entry, Lexicon, DiatopicVariation, Word)

import csv
import os.path


def get_src_language_from_lexicon_code(lex_code):
    return lex_code[:2]


def get_dst_language_from_lexicon_code(lex_code):
    return lex_code[3:]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon code where data will be exported from",
        )

        parser.add_argument(
            'variation_name', type=str,
            help="The variation name of the variation chosen to export the data",
        )

        parser.add_argument(
            'output_file', type=str,
            help='Name of file where data will be written to. (must be a csv file)'
        )

    def handle(self, *args, **options):
        self.lexicon_code = options['lexicon_code']
        self.variation_name = options['variation_name']
        self.output_file = options['output_file']
        # check that a lexicon with that code exist
        try:
            src = get_src_language_from_lexicon_code(self.lexicon_code)
            dst = get_dst_language_from_lexicon_code(self.lexicon_code)

            self.lexicon = Lexicon.objects.get(src_language=src, dst_language=dst)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        try:
            self.variation = DiatopicVariation.objects.get(name=self.variation_name)
        except DiatopicVariation.DoesNotExist:
            raise CommandError('Error: There is not a diatopic variation with that name: ' + self.variation_name)

        # check if csv file already exists
        if os.path.isfile(self.output_file):
            raise CommandError('Error: A csv with that name already exists: ' + self.output_file)

        self.write_to_csv_file()

    def write_to_csv_file(self):

        entry_list = Entry.objects.filter(variation=self.variation).values('word__term').distinct().order_by('word__term')

        word_list = []
        for entry in entry_list:
            word_list.append(Word.objects.get(term=entry['word__term']))

        with open(self.output_file, 'w') as outfile:

            fieldnames = [
                'word',
                'gramcats',
                'translation',
            ]

            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')

            for word in word_list:

                to_write = {'word': word.term}

                to_write['gramcats'] = ' // '.join(Entry.objects.filter(word=word, variation=self.variation)
                                                   .values_list('gramcats__abbreviation', flat=True)
                                                   .distinct().order_by('gramcats__abbreviation'))

                to_write['translation'] = ' // '.join(Entry.objects.filter(word=word, variation=self.variation)    
                                                      .values_list('translation', flat=True))

                writer.writerow(to_write)
