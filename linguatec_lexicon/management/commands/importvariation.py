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
            help='Diatopical variation of the data to be imported'
        )
        parser.add_argument(
            '--dry-run', action='store_true', dest='dry_run',
            help="Just validate input file; don't actually import to database.",
        )

    def clean_variation(self, value):
        if self.dry_run:
            return value

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

        # validate input_file
        _, file_extension = os.path.splitext(self.input_file)
        if file_extension.lower() != '.xlsx':
            raise CommandError(
                'Unexpected filetype "{}". Should be an Excel document (XLSX)'.format(file_extension))

        self.variation = self.clean_variation(options['variation'])

        # check that GramaticalCategories are initialized
        if not GramaticalCategory.objects.all().exists():
            raise CommandError(
                "There isn't any GramaticalCategory in the database. "
                "Gramatical Categories should be initialized before importing "
                "data for example running manage.py importgramcat."
            )

        self.xlsx = pd.read_excel(self.input_file, header=None, usecols="A:C",
                                  names=['term', 'gramcats', 'translations'])
        self.populate_models()

        if self.errors:
            self.stdout.write(self.style.ERROR(
                "Detected {} errors!".format(len(self.errors))))
            if self.verbosity > 2:
                for error in self.errors:
                    self.stdout.write(self.style.ERROR(json.dumps(error)))
        else:
            if not self.dry_run:
                # Write data into the database
                self.write_to_database()
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported file "{}" of diatopic variation "{}"'.format(self.input_file, self.variation)))

        if self.verbosity > 1:
            self.stdout.write(
                "Excel stats: {} rows | {} valid rows | {} invalid rows".format(
                    len(self.xlsx.index),
                    len(self.cleaned_data),
                    len(self.errors),
                )
            )

    def populate_models(self):
        self.errors = []
        self.cleaned_data = []

        for row in self.xlsx.itertuples():
            word = self.retrieve_word(row.Index + 1, row.term)
            if word is None:
                continue

            try:
                gramcats = self.retrieve_gramcats(word, row.gramcats)
                self.populate_entries(word, gramcats, row.translations)
            except:
                continue

            self.cleaned_data.append(word)

    def populate_entries(self, word, gramcats, translations_raw):
        word.clean_entries = []

        try:
            translations_list = translations_raw.split('//')
        except AttributeError as e:
            # e.g. empty cell is translated as float(nan)
            self.errors.append({
                "word": word.term,
                "column": "C",
                "message": 'Word "{}" contains empty or invalid translations.'.format(word.term)
            })
            raise ValueError(e)

        for translation in translations_list:
            entry = Entry(word=word, translation=translation.strip(),
                          variation=self.variation)
            entry.clean_gramcats = gramcats
            word.clean_entries.append(entry)

    def retrieve_gramcats(self, word, gramcats_raw):
        gramcats = []
        if not gramcats_raw:
            message = "missing gramatical category"
            self.errors.append({
                "word": word.term,
                "column": "B",
                "message": message
            })
            raise ValueError(message)

        for abbr in gramcats_raw.split("//"):
            abbr = abbr.strip()
            try:
                gramcats.append(
                    GramaticalCategory.objects.get(abbreviation=abbr))
            except GramaticalCategory.DoesNotExist:
                message = "unkown gramatical category '{}'".format(abbr)
                self.errors.append({
                    "word": word.term,
                    "column": "B",
                    "message": message
                })
                raise ValueError(message)

        return gramcats

    def retrieve_word(self, row_number, term_raw):
        # 1) exact match
        try:
            term = term_raw.strip()
        except AttributeError:
            # e.g. empty cell is translated as float(nan)
            self.errors.append({
                "word": term_raw,
                "column": "A",
                "message": 'Empty or invalid value at row {}.'.format(row_number)
            })
            return None
        try:
            return Word.objects.get(term=term)
        except Word.DoesNotExist:
            pass

        # 2) handle cases where only masculine form has been included
        # instead of both. e.g. delicado --> delicado/a
        try:
            return Word.objects.get(term=term + "/a")
        except Word.DoesNotExist:
            # 3) trigam similarity (only as suggestion)
            message = 'Word "{}" not found in the database.'.format(term)
            suggestions = None
            qs = Word.objects.search(term)[:4]
            if qs.exists():
                suggestions = ', '.join(qs.values_list('term', flat=True))
                message += ' Did you mean: {}?'.format(suggestions)

            self.errors.append({
                "word": term,
                "column": "A",
                "message": message,
                "suggestions": suggestions
            })


    def write_to_database(self):
        count_entries = 0
        for word in self.cleaned_data:
            for entry in word.clean_entries:
                entry.save()
                entry.gramcats.set(entry.clean_gramcats)
                count_entries += 1

        self.stdout.write("Imported: {} entries of {} words.".format(
            count_entries, len(self.cleaned_data)))
