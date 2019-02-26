import json
import pandas as pd

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import (
    Entry, Example, Lexicon, GramaticalCategory, VerbalConjugation, Word)
from linguatec_lexicon.validators import validate_column_verb_conjugation


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


def is_verb(gramcats):
    for gramcat in gramcats:
        if gramcat.abbreviation.startswith('v.'):
            return True
    return False


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)
        parser.add_argument(
            '--dry-run', action='store_true', dest='dry_run',
            help="Just validate input file; don't actually import to database.",
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        self.input_file = options['input_file']

        # check that GramaticalCategories are initialized
        if not GramaticalCategory.objects.all().exists():
            raise CommandError(
                "There isn't any GramaticalCategory in the database. "
                "Gramatical Categories should be initialized before importing "
                "data for example running manage.py importgramcat."
            )

        self.stdout.write("INFO\tinput file: %s\n" % self.input_file, ending='')

        db = self.read_input_file()

        # TODO add arg to print (or not gramcats)
        #gramcats = extract_gramcats(db)

        self.populate_models(db)

        if self.errors:
            self.stdout.write(self.style.ERROR(
                "Detected {} errors!".format(len(self.errors))))
            if self.verbosity >= 2:
                for error in self.errors:
                    self.stdout.write(self.style.ERROR(json.dumps(error)))

        elif not self.dry_run:
            # Write data into the database
            self.write_to_database()

    def read_input_file(self):
        df = pd.DataFrame()

        xlsx = pd.ExcelFile(self.input_file)

        for sheet in xlsx.sheet_names:
            # we define na_values and keep_default_na because defaults na_values
            # includes empty string. We don't want that pandas replaces empty
            # cells with 'nan'
            partial = xlsx.parse(sheet, header=None, usecols='A:F')
            # names=['colA', 'colB', 'colC', 'colD', 'colE', 'colF'])
            df = df.append(partial, ignore_index=True, sort=False)

        df_obj = df.select_dtypes(['object'])
        df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
        df = df.fillna('')  # replace NaN with blank string

        return df

    def get_or_create_word(self, term):
        for word in self.cleaned_data:
            if word.term == term:
                return (False, word)

        new_word = Word(term=term)
        new_word.clean_entries = []
        return (True, new_word)

    def populate_word(self, w_str):
        # avoid duplicated word.term
        created, word = self.get_or_create_word(w_str)
        if created:
            self.cleaned_data.append(word)

        return word

    def populate_gramcats(self, word, g_str):
        gramcats = []
        if not g_str:
            self.errors.append({
                "word": word.term,
                "column": "B",
                "message": "missing gramatical category"
            })
        else:
            for abbr in g_str.split("//"):
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
        word.is_verb = is_verb(gramcats)
        return gramcats

    def populate_models(self, db):
        self.errors = []
        self.cleaned_data = []
        for row in db.itertuples(name=None):
            # itertuples by default return the index as the first element of the tuple.

            # filter empty rows
            # TODO how to ignore empty rows in an elegant way?
            if pd.isnull(row) or pd.isna(row[1]) or pd.isnull(row[1]) or row[1] == '':
                continue

            # column A is word (required)
            word = self.populate_word(row[1])

            # column B is gramcat (required)
            gramcats = self.populate_gramcats(word, row[2])

            # column C is entry (required)
            en_str = row[3]
            en_strs = en_str.split(' // ')
            for s in en_strs:  # subelement
                entry = Entry(word=word, translation=s)
                entry.clean_gramcats = gramcats
                entry.clean_examples = []
                word.clean_entries.append(entry)

            # column E is example (optional)
            try:
                ex_str = row[5]
            except IndexError:
                continue
            else:
                if pd.notnull(ex_str) and ex_str != '':
                    ex_strs = [x.strip() for x in ex_str.split('//')]
                    if len(word.clean_entries) < len(ex_strs):
                        self.errors.append({
                            "word": word.term,
                            "column": "E",
                            "message": "there are more examples '{}' than entries'{}'".format(
                                len(word.clean_entries), len(ex_strs))
                        })
                        continue  # invalid format, don't try to extract it!
                    for i, value in enumerate(ex_strs):  # subelement
                        we = word.clean_entries[i]  # word entry
                        if value:
                            # TODO could be several examples separated by ';'
                            we.clean_examples.append(Example(phrase=value))

            # column F is verb conjugation
            try:
                conjugation_str = row[6]
            except IndexError:
                continue
            else:
                # check if word is a verb
                if conjugation_str and not word.is_verb:
                    self.errors.append({
                        "word": word.term,
                        "column": "F",
                        "message": "only verbs can have verbal conjugation data",
                    })
                    continue

                raw_conjugations = [x.strip()
                                    for x in conjugation_str.split('//')]

                # check number of conjugations VS number of entries
                if len(word.clean_entries) < len(raw_conjugations):
                    self.errors.append({
                        "word": word.term,
                        "column": "F",
                        "message": "there are more conjugations '{}' than entries'{}'".format(
                            len(word.clean_entries), len(conjugation_str))
                    })
                    continue  # invalid format, don't try to extract it!

                for i, raw_conjugation in enumerate(raw_conjugations):
                    if raw_conjugation:
                        try:
                            validate_column_verb_conjugation(raw_conjugation)
                        except ValidationError as e:
                            self.errors.append({
                                "word": word.term,
                                "column": "F",
                                "message": str(e.message),
                            })
                        else:
                            word.clean_entries[i].clean_conjugation = VerbalConjugation(
                                raw=raw_conjugation)


    def write_to_database(self):
        # TODO allow to use an existing Lexicon or pass as args the new Lexicon parameters
        lex, _ = Lexicon.objects.get_or_create(
            src_language="es",
            dst_language="ar",
            defaults={'name': "diccionario linguatec"}
        )

        count_words = 0
        count_entries = 0
        count_examples = 0
        for word in self.cleaned_data:
            word.lexicon_id = lex.pk
            word.save()
            count_words += 1

            for entry in word.clean_entries:
                entry.word_id = word.pk
                entry.save()
                entry.gramcats.set(entry.clean_gramcats)
                count_entries += 1

                for example in entry.clean_examples:
                    example.entry_id = entry.pk
                    example.save()
                    count_examples += 1

                try:
                    entry.clean_conjugation.entry_id = entry.pk
                    entry.clean_conjugation.save()
                except AttributeError:
                    pass

        self.stdout.write("Imported: %s words, %s entries, %s examples" %
                          (count_words, count_entries, count_examples))
