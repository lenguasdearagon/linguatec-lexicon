import json
import os

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import (DiatopicVariation, Entry,
                                      GramaticalCategory, Word)


class Command(BaseCommand):
    help = 'Imports diatopic variation Excel into the database'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)
        parser.add_argument(
            '--variation',
            required=True,
            help='Diatopical variation of the data to be imported'
        )

    def handle(self, *args, **options):
        self.input_file = options['input_file']
        self.verbosity = options['verbosity']

        # validate input_file
        _, file_extension = os.path.splitext(self.input_file)
        if file_extension.lower() != '.xlsx':
            raise CommandError('Unexpected filetype "{}". Should be an Excel document (XLSX)'.format(file_extension))

        # validate variation
        try:
            self.variation = DiatopicVariation.objects.get(name=options['variation'])
        except DiatopicVariation.DoesNotExist:
            raise CommandError('Diatopic variation "{}" does not exist'.format(self.variation))

        # check that GramaticalCategories are initialized
        if not GramaticalCategory.objects.all().exists():
            raise CommandError(
                "There isn't any GramaticalCategory in the database. "
                "Gramatical Categories should be initialized before importing "
                "data for example running manage.py importgramcat."
            )


        self.xlsx = pd.read_excel(self.input_file, header=None, names=['term', 'gramcats', 'translations'])
        self.populate_models()

        if self.errors:
            self.stdout.write(self.style.ERROR(
                "Detected {} errors!".format(len(self.errors))))
            if self.verbosity >= 2:
                for error in self.errors:
                    self.stdout.write(self.style.ERROR(json.dumps(error)))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported file "{}" of diatopic variation "{}"'.format(self.input_file, self.variation)))


    def populate_models(self):
        self.errors = []
        self.cleaned_data = []

        for row in self.xlsx.itertuples():
            word = self.retrieve_word(row.term)
            if word is None:
                continue

            gramcats = self.retrieve_gramcats(word, row.gramcats)
            self.populate_entries(word, gramcats, row.translations)
            self.cleaned_data.append(word)

            # TODO REMOVE XXX
            if(row[0] == 10):
                    break

    def populate_entries(self, word, gramcats, translations_raw):
        word.clean_entries = []
        for translation in translations_raw.split('//'):
            entry = Entry(word=word, translation=translation.strip(), variation=self.variation)
            entry.clean_gramcats = gramcats
            word.clean_entries.append(entry)

    def retrieve_gramcats(self, word, gramcats_raw):
        gramcats = []
        if not gramcats_raw:
            self.errors.append({
                "word": word.term,
                "column": "B",
                "message": "missing gramatical category"
            })
        else:
            for abbr in gramcats_raw.split("//"):
                abbr = abbr.strip()
                try:
                    gramcats.append(
                        GramaticalCategory.objects.get(abbreviation=abbr))
                except GramaticalCategory.DoesNotExist:
                    self.errors.append({
                        "word": word.term,
                        "column": "B",
                        "message": "unkown gramatical category '{}'".format(abbr)
                    })

        return gramcats


    def retrieve_word(self, term_raw):
        term = term_raw.strip()
        try:
            return Word.objects.get(term=term)
        except Word.DoesNotExist:
            self.errors.append({
                "word": term,
                "column": "A",
                "message": 'Word "{}" not found in the database.'.format(term)
            })
