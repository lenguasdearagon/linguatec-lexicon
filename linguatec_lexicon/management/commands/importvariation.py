import json
import os

from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import (DiatopicVariation, Lexicon)

from linguatec_lexicon.importers import importvariation


def get_src_language_from_lexicon_code(lex_code):
    return lex_code[:2]


def get_dst_language_from_lexicon_code(lex_code):
    return lex_code[3:]


class Command(BaseCommand):
    help = 'Imports diatopic variation Excel into the database'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon where data will be imported",
        )
        parser.add_argument(
            '--variation',
            help='Diatopical variation of the data to be imported'
        )
        parser.add_argument(
            '--dry-run', action='store_true', dest='dry_run',
            help="Just validate input file; don't actually import to database.",
        )

    def clean_variation(self, value):
        if self.dry_run:
            return None  # discard value because doesn't affect to data validation

        # validate variation
        try:
            return DiatopicVariation.objects.get(name=value)
        except DiatopicVariation.DoesNotExist:
            raise CommandError(
                'Diatopic variation "{}" does not exist'.format(value))

    def handle(self, *args, **options):
        self.input_file = options['input_file']
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        self.lexicon_code = options['lexicon_code']

        # validate input_file
        _, file_extension = os.path.splitext(self.input_file)
        if file_extension.lower() != '.xlsx':
            raise CommandError(
                'Unexpected filetype "{}". Should be an Excel document (XLSX)'.format(file_extension))

        self.variation = self.clean_variation(options['variation'])

        # check that a lexicon with that code exist
        try:
            src = get_src_language_from_lexicon_code(self.lexicon_code)
            dst = get_dst_language_from_lexicon_code(self.lexicon_code)

            self.lexicon = Lexicon.objects.get(src_language=src, dst_language=dst)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        if self.dry_run:
            self.errors, self.cleaned_data = importvariation(self.input_file, self.lexicon.pk,
                                                             self.variation, self.dry_run)
        else:
            self.errors, self.cleaned_data = importvariation(self.input_file, self.lexicon.pk,
                                                             self.variation.pk, self.dry_run)

        if self.errors:
            self.stdout.write(self.style.ERROR(
                "Detected {} errors!".format(len(self.errors))))
            if self.verbosity > 2:
                for error in self.errors:
                    self.stdout.write(self.style.ERROR(json.dumps(error)))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported file "{}" of diatopic variation "{}"'.format(self.input_file, options['variation'])))

        if self.verbosity > 1:
            self.stdout.write(
                "Excel stats: {} rows | {} valid rows | {} invalid rows".format(
                    sum([len(sheet.index) for sheet in self.xlsx.values()]),
                    len(self.cleaned_data),
                    len(self.errors),
                )
            )
