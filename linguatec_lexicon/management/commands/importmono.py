from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook

from linguatec_lexicon.models import Entry, Lexicon, Word


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon where data will be imported",
        )
        parser.add_argument('input_file', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        self.input_file = options['input_file']
        self.lexicon_code = options['lexicon_code']

        # check that a lexicon with that code exist
        try:
            self.lexicon = Lexicon.objects.get_by_slug(self.lexicon_code)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        # self.xlsx = pd.read_excel(self.input_file, sheet_name=None, header=None, usecols="A:E",
        #                           names=["term", "url", "etimol", "def", "def2"])

        self.xlsx = load_workbook(self.input_file, read_only=True)
        sheet = self.xlsx.active

        for i, row in enumerate(sheet.iter_rows()):
            if i == 0:
                continue

            term = row[0].value
            url = row[1].value,
            etimol = row[2].value
            definition = row[3].value
            definition2 = row[4].value

            word_data = {
                "term": term,
                # "etimol": etimol,     # TODO: Add etimol to Word model
            }

            try:
                word = Word(lexicon=self.lexicon, **word_data)
                word.full_clean(exclude=["slug"])
                word.save()
            except ValidationError as e:
                errors = e.message_dict
                continue

            entries = [Entry(word=word, translation=definition)]
            if definition2:
                entries.append(Entry(word=word, translation=definition2))
            word.entries.bulk_create(entries)
