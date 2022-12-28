import os

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.functional import cached_property

from linguatec_lexicon.models import (DiatopicVariation, Entry,
                                      GramaticalCategory, Lexicon, Word)


class Command(BaseCommand):
    help = 'Imports diatopic variation Excel into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon where data will be imported",
        )
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

        # check that GramaticalCategories are initialized
        if not GramaticalCategory.objects.all().exists():
            raise CommandError(
                "There isn't any GramaticalCategory in the database. "
                "Gramatical Categories should be initialized before importing "
                "data for example running manage.py importgramcat."
            )

        # check that a lexicon with that code exist
        try:
            self.lexicon = Lexicon.objects.get_by_slug(self.lexicon_code)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        self.xlsx = pd.read_excel(self.input_file, sheet_name=None, header=None, usecols="A:C",
                                  names=['term', 'gramcats', 'translations'])
        self.populate_models()

        if self.errors:
            self.stdout.write(self.style.ERROR(
                "Detected {} errors!".format(len(self.errors))))
            if self.verbosity > 2:
                for error in self.errors:
                    values = [str(value) or '' for value in error.values()]
                    self.stdout.write(self.style.ERROR('    '.join(values)))
        else:
            if not self.dry_run:
                # Write data into the database
                self.write_to_database()
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported file "{}" of diatopic variation "{}"'.format(self.input_file, options['variation'])))

        if self.verbosity > 1:
            self.stdout.write(
                "Excel stats: {} rows | {} valid rows | {} invalid rows".format(
                    sum([len(sheet.index) for sheet in self.xlsx.values()]),
                    self.words_count,
                    len(self.errors),
                )
            )

    def populate_models(self):
        self.errors = []
        self.entries = []
        self.words_count = 0

        for sheet_name, sheet in self.xlsx.items():
            for row in sheet.itertuples():
                word = self.retrieve_word(row.Index + 1, row.term)
                if word is None:
                    continue

                try:
                    gramcats = self.retrieve_gramcats(word, row.gramcats)
                    self.populate_entries(word, gramcats, row.translations)
                except ValidationError as e:
                    message = e.message % e.params if e.params else e.message
                    self.errors.append({
                        "word": word.term,
                        "column": "{}!{}".format(sheet_name, e.code),
                        "message": message,
                    })
                    continue

                self.words_count += 1

    def populate_entries(self, word, gramcats, translations_raw):
        word.clean_entries = []

        try:
            translations_list = translations_raw.split('//')
        except AttributeError:
            # e.g. empty cell is translated as float(nan)
            message = 'Word %(word)s contains empty or invalid translations.'
            raise ValidationError(message, code='C', params={'word': word.term})

        for translation in translations_list:
            entry = Entry(word=word, translation=translation.strip(),
                          variation=self.variation)
            entry.clean_gramcats = gramcats
            word.clean_entries.append(entry)
            self.entries.append(entry)

    def retrieve_gramcats(self, word, gramcats_raw):
        clean_gramcats = self.parse_or_get_default_gramcats(word, gramcats_raw)

        gramcats = []
        for abbr in clean_gramcats:
            try:
                gramcats.append(self.retrieve_gramcat(abbr))
            except GramaticalCategory.DoesNotExist:
                message = "unkown gramatical category %(value)s"
                raise ValidationError(message, code='B', params={'value': abbr})

        return gramcats

    def parse_or_get_default_gramcats(self, word, gramcats_raw):
        if pd.isnull(gramcats_raw):
            # provide default value
            clean_gramcats = word.gramcats()
            if len(clean_gramcats) == 0:
                message = "missing gramatical category"
                raise ValidationError(message, code='B')
            return clean_gramcats

        clean_gramcats = [abbr.strip() for abbr in gramcats_raw.split("//")]
        return clean_gramcats

    def retrieve_gramcat(self, abbr):
        try:
            return self._gramcats[abbr]
        except KeyError:
            raise GramaticalCategory.DoesNotExist()

    @cached_property
    def _gramcats(self):
        # one big query vs N queries where N is the number of entries
        return {g.abbreviation: g for g in GramaticalCategory.objects.all()}

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
            return self.get_word(term)
        except Word.DoesNotExist:
            pass

        # 2) handle cases where only masculine form has been included
        # instead of both. e.g. delicado --> delicado/a
        try:
            return self.get_word(term + "/a")
        except Word.DoesNotExist:
            # 3) trigam similarity (only as suggestion)
            message = 'Word "{}" not found in the database.'.format(term)
            suggestions = None
            qs = Word.objects.search(term, self.lexicon.code)[:4]
            if qs.exists():
                suggestions = ', '.join(qs.values_list('term', flat=True))
                message += ' Did you mean: {}?'.format(suggestions)

            self.errors.append({
                "word": term,
                "column": "A",
                "message": message,
                "suggestions": suggestions
            })

    def get_word(self, term):
        try:
            return self._words[term]
        except KeyError:
            raise Word.DoesNotExist()

    @cached_property
    def _words(self):
        qs = Word.objects.filter(lexicon=self.lexicon)
        return {w.term: w for w in qs}

    @transaction.atomic
    def write_to_database(self):
        Entry.objects.bulk_create(self.entries, batch_size=100)

        for entry in self.entries:
            entry.gramcats.set(entry.clean_gramcats)

        count_entries = len(self.entries)
        self.stdout.write("Imported: {} entries of {} words.".format(
            count_entries, self.words_count))
