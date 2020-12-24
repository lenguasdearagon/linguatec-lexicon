from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.exporters import write_to_csv_file_data

from linguatec_lexicon.models import (Lexicon)

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
            self.lexicon = Lexicon.objects.get_by_code(self.lexicon_code)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        # check if csv file already exists
        if os.path.isfile(self.output_file):
            raise CommandError('Error: A csv with that name already exists: ' + self.output_file)

        write_to_csv_file_data(self.lexicon.pk, self.output_file)
