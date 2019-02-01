import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import GramaticalCategory


class Command(BaseCommand):
    help = 'Imports Gramatical Categories from a CSV file'
    missing_args_message = (
        "No CSV file specified. Please provide the path of at least "
        "one file in the command line."
    )

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='csv_file',
                            nargs='+', help='CSV files.')
        parser.add_argument(
            '--purge', action='store_true', dest='purge',
            help='Remove old Gramatical Categories before performing '
                 'the import.'
        )


    def handle(self, *csv_files, **options):
        self.verbosity = options['verbosity']
        self.purge_gramcat = options['purge']

        if self.purge_gramcat:
            deleted, _ = GramaticalCategory.objects.all().delete()
            if self.verbosity >= 1:
                self.stdout.write(
                    "Purged %d object(s) from database" % deleted
                )

        self.loaddata(csv_files)

        if self.verbosity >= 1:
            self.stdout.write(
                "Imported %d object(s) from %d file(s)"
                % (self.loaded_object_count, self.csv_count)
            )

    def loaddata(self, csv_files):
        # Keep a count of the installed objects and files
        self.csv_count = 0
        self.loaded_object_count = 0

        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            gramcats = []
            for row in df.itertuples(name=None):
                gramcats.append(
                    GramaticalCategory(
                        abbreviation=row[1], title=row[2])
                )
                self.loaded_object_count += 1

            GramaticalCategory.objects.bulk_create(gramcats)
            self.csv_count += 1
