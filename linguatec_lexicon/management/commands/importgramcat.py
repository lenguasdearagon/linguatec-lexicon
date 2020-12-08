from django.core.management.base import BaseCommand

from linguatec_lexicon.tasks import loaddatagramcats

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

        self.loaded_object_count, self.csv_count = loaddatagramcats(csv_files)

        if self.verbosity >= 1:
            self.stdout.write(
                "Imported %d object(s) from %d file(s)"
                % (self.loaded_object_count, self.csv_count)
            )
