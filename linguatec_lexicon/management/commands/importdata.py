import json
import pandas as pd

from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import Lexicon

from linguatec_lexicon.importers import import_data


def split_data_frame_list(df, target_column):
    # thanks src https://gist.github.com/jlln/338b4b0b55bd6984f883#gistcomment-2676729
    """
    Splits a column with lists into rows

    Keyword arguments:
        df -- dataframe
        target_column -- name of column that contains lists
    """

    # create a new dataframe with each item in a seperate column, dropping rows with missing values
    col_df = pd.DataFrame(df[target_column].dropna(
    ).tolist(), index=df[target_column].dropna().index)

    # create a series with columns stacked as rows
    stacked = col_df.stack()

    # rename last column to 'idx'
    index = stacked.index.rename(names="idx", level=-1)
    new_df = pd.DataFrame(stacked, index=index, columns=[target_column])
    return new_df


def extract_gramcats(db):
    db_s = split_data_frame_list(db, 1)
    # src https://datascience.stackexchange.com/questions/29840/how-to-count-grouped-occurrences/29842#29842
    gramcats = db_s.groupby([1]).size().to_frame('count').reset_index()
    print('=========================')
    print('Gramatical categories')
    print(gramcats)
    print('=========================')
    return gramcats


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon where data will be imported",
        )
        parser.add_argument(
            '--dry-run', action='store_true', dest='dry_run',
            help="Just validate input file; don't actually import to database.",
        )
        parser.add_argument(
            '--allow-partial', action='store_true', dest='allow_partial',
            help="Allow verbs with partial or unknown format conjugations. USE WITH CAUTION",
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        self.input_file = options['input_file']
        self.allow_partial = options['allow_partial']
        self.lexicon_code = options['lexicon_code']

        # check that a lexicon with that code exist
        try:
            self.lexicon = Lexicon.objects.get_by_code(self.lexicon_code)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)

        self.stdout.write("INFO\tinput file: %s\n" % self.input_file)

        # TODO add arg to print (or not gramcats)
        # gramcats = extract_gramcats(db)

        self.errors = import_data(self.input_file, self.lexicon.pk,
                                  self.dry_run, self.allow_partial)

        if self.errors:
            self.stdout.write(self.style.ERROR(
                "Detected {} errors!".format(len(self.errors))))
            if self.verbosity >= 2:
                for error in self.errors:
                    self.stdout.write(self.style.ERROR(json.dumps(error)))
