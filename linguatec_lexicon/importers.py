import pandas as pd
import sys

from linguatec_lexicon.models import (Entry, GramaticalCategory, Word,
                                      Lexicon, DiatopicVariation, Example,
                                      VerbalConjugation, ImportsInfo)


from django.core.exceptions import ValidationError
from django.core.management.base import CommandError

from django.db import IntegrityError

from linguatec_lexicon.validators import validate_column_verb_conjugation


def load_gramcats(csv_files, imports_info_id):
    # Keep a count of the installed objects and files
    csv_count = 0
    loaded_object_count = 0

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, engine='python')
        gramcats = []
        for row in df.itertuples(name=None):
            gramcats.append(
                GramaticalCategory(
                    abbreviation=row[1], title=row[2])
            )
            loaded_object_count += 1

        GramaticalCategory.objects.bulk_create(gramcats)
        csv_count += 1

    ii = ImportsInfo.objects.get(pk=imports_info_id)
    ii.status = ImportsInfo.COMPLETED
    ii.num_rows = loaded_object_count
    ii.save()

    return loaded_object_count, csv_count


def import_variation(input_file, lexicon, variation, dry_run, imports_info_id):

    errors = []
    ii = ImportsInfo.objects.get(pk=imports_info_id)

    def retrieve_word(row_number, term_raw):
        # 1) exact match
        try:
            term = term_raw.strip()
        except AttributeError:
            # e.g. empty cell is translated as float(nan)
            errors.append({
                "word": term_raw,
                "column": "A",
                "message": 'Empty or invalid value at row {}.'.format(row_number)
            })
            return None
        try:
            return Word.objects.get(term=term, lexicon=lexicon)
        except Word.DoesNotExist:
            pass

        # 2) handle cases where only masculine form has been included
        # instead of both. e.g. delicado --> delicado/a
        try:
            return Word.objects.get(term=term + "/a", lexicon=lexicon)
        except Word.DoesNotExist:
            # 3) trigam similarity (only as suggestion)
            message = 'Word "{}" not found in the database.'.format(term)
            suggestions = None
            qs = Word.objects.search(term, Lexicon.objects.get(pk=lexicon).code)[:4]
            if qs.exists():
                suggestions = ', '.join(qs.values_list('term', flat=True))
                message += ' Did you mean: {}?'.format(suggestions)

            errors.append({
                "word": term,
                "column": "A",
                "message": message,
                "suggestions": suggestions
            })

    def parse_or_get_default_gramcats(word, gramcats_raw):
        if pd.isnull(gramcats_raw):
            # provide default value
            clean_gramcats = word.gramcats()
            if len(clean_gramcats) == 0:
                message = "missing gramatical category"
                ii.status = ImportsInfo.FAILED
                ii.errors = message
                ii.save()
                raise ValidationError(message, code='B')
            return clean_gramcats

        clean_gramcats = [abbr.strip() for abbr in gramcats_raw.split("//")]
        return clean_gramcats

    def retrieve_gramcats(word, gramcats_raw):
        clean_gramcats = parse_or_get_default_gramcats(word, gramcats_raw)

        gramcats = []
        for abbr in clean_gramcats:
            try:
                gramcats.append(
                    GramaticalCategory.objects.get(abbreviation=abbr))
            except GramaticalCategory.DoesNotExist:
                message = "unkown gramatical category %(value)s"
                ii.status = ImportsInfo.FAILED
                ii.errors = message
                ii.save()
                raise ValidationError(message, code='B', params={'value': abbr})

        return gramcats

    def populate_entries(word, gramcats, translations_raw):
        word.clean_entries = []

        try:
            translations_list = translations_raw.split('//')
        except AttributeError:
            # e.g. empty cell is translated as float(nan)
            message = 'Word %(word)s contains empty or invalid translations.'
            ii.status = ImportsInfo.FAILED
            ii.errors = message
            ii.save()
            raise ValidationError(message, code='C', params={'word': word.term})

        for translation in translations_list:
            entry = Entry(word=word, translation=translation.strip(),
                          variation=DiatopicVariation.objects.get(pk=variation))
            entry.clean_gramcats = gramcats
            word.clean_entries.append(entry)

    def populate_models(xlsx):
        cleaned_data = []

        for sheet_name, sheet in xlsx.items():
            for row in sheet.itertuples():
                word = retrieve_word(row.Index + 1, row.term)
                if word is None:
                    continue

                try:
                    gramcats = retrieve_gramcats(word, row.gramcats)
                    populate_entries(word, gramcats, row.translations)
                except ValidationError as e:
                    message = e.message % e.params if e.params else e.message
                    errors.append({
                        "word": word.term,
                        "column": "{}!{}".format(sheet_name, e.code),
                        "message": message,
                    })
                    continue

                cleaned_data.append(word)
        return cleaned_data

    def write_to_database(cleaned_data):
        count_entries = 0
        for word in cleaned_data:
            for entry in word.clean_entries:
                entry.save()
                entry.gramcats.set(entry.clean_gramcats)
                count_entries += 1

        sys.stdout.write("Imported: {} entries of {} words.".format(
            count_entries, len(cleaned_data)))

        return count_entries

    # check that GramaticalCategories are initialized
    if not GramaticalCategory.objects.all().exists():

        ii.status = ImportsInfo.FAILED
        ii.errors = ("There isn't any GramaticalCategory in the database. " +
                     "Gramatical Categories should be initialized before importing " +
                     "data for example running manage.py importgramcat.")

        ii.save()
        raise CommandError(
            "There isn't any GramaticalCategory in the database. "
            "Gramatical Categories should be initialized before importing "
            "data for example running manage.py importgramcat."
        )

    xlsx = pd.read_excel(input_file, sheet_name=None, header=None, usecols="A:C",
                         names=['term', 'gramcats', 'translations'])
    cleaned_data = populate_models(xlsx)

    if not dry_run:
        count_entries = write_to_database(cleaned_data)

        ii.status = ImportsInfo.COMPLETED
        ii.num_rows = count_entries

    if errors:
        ii.status = ImportsInfo.COMPLETED_WITH_ERRORS
        ii.errors = errors

    ii.save()
    return errors, cleaned_data


def import_data(input_file, lexicon_pk, dry_run, allow_partial, imports_info_id):

    errors = []
    cleaned_data = {}
    ii = ImportsInfo.objects.get(pk=imports_info_id)

    def read_input_file():
        df = pd.DataFrame()

        xlsx = pd.ExcelFile(input_file)

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

    def get_or_create_word(term):
        try:
            return (False, cleaned_data[term])
        except KeyError:
            new_word = Word(term=term)
            new_word.clean_entries = []
            return (True, new_word)

    def populate_word(w_str):
        # avoid duplicated word.term
        created, word = get_or_create_word(w_str)
        if created:
            cleaned_data[word.term] = word

        return word

    def is_verb(gramcats):
        for gramcat in gramcats:
            if (gramcat.abbreviation.startswith('v.')
                    or gramcat.abbreviation in ['expr.', 'per. vl.', 'loc. vl.']):
                return True
        return False

    def populate_gramcats(word, g_str):
        gramcats = []
        if not g_str:
            errors.append({
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
                    errors.append({
                        "word": word.term,
                        "column": "B",
                        "message": "unkown gramatical category '{}'".format(abbr)
                    })
        word.is_verb = is_verb(gramcats)
        return gramcats

    def populate_entries(word, gramcats, entries_str):
        for translation in entries_str.split('//'):
            entry = Entry(word=word, translation=translation.strip())
            entry.clean_gramcats = gramcats
            entry.clean_examples = []
            word.clean_entries.append(entry)

    def populate_examples(word, ex_str):
        if pd.isnull(ex_str) or ex_str == '':
            return

        ex_strs = [x.strip() for x in ex_str.split('//')]
        if len(word.clean_entries) < len(ex_strs):
            errors.append({
                "word": word.term,
                "column": "E",
                "message": "there are more examples '{}' than entries'{}'".format(
                    len(ex_strs), len(word.clean_entries))
            })
            # invalid format, don't try to extract it!
            return

        for i, value in enumerate(ex_strs):  # subelement
            we = word.clean_entries[i]  # word entry
            if value:
                # TODO could be several examples separated by ';'
                we.clean_examples.append(Example(phrase=value))

    def populate_verbal_conjugation(word, gramcats, conjugation_str):
        # check if word is a verb
        if conjugation_str and not word.is_verb:
            gramcats = [x.abbreviation for x in gramcats]
            errors.append({
                "word": word.term,
                "column": "F",
                "message": "only verbs can have verbal conjugation data (found {})".format(gramcats),
            })
            return

        raw_conjugations = [x.strip()
                            for x in conjugation_str.split('//')]

        # check number of conjugations VS number of entries
        if len(word.clean_entries) < len(raw_conjugations):
            errors.append({
                "word": word.term,
                "column": "F",
                "message": "there are more conjugations '{}' than entries'{}'".format(
                    len(word.clean_entries), len(conjugation_str))
            })
            # invalid format, don't try to extract it!
            return

        for i, raw_conjugation in enumerate(raw_conjugations):
            if raw_conjugation:
                try:
                    validate_column_verb_conjugation(raw_conjugation)
                except ValidationError as e:
                    if not allow_partial:
                        errors.append({
                            "word": word.term,
                            "column": "F",
                            "message": str(e.message),
                        })
                    partial = True
                else:
                    partial = False
                # workaround issue 66 allow partial conjugations (or unformated data)
                if not partial or partial and allow_partial:
                    word.clean_entries[i].clean_conjugation = VerbalConjugation(
                        raw=raw_conjugation)

    def populate_models(db):
        for row in db.itertuples(name=None):
            # itertuples by default return the index as the first element of the tuple.

            # filter empty rows
            # TODO how to ignore empty rows in an elegant way?
            if pd.isnull(row) or pd.isna(row[1]) or pd.isnull(row[1]) or row[1] == '':
                continue

            # column A is word (required)
            word = populate_word(row[1])

            # column B is gramcat (required)
            gramcats = populate_gramcats(word, row[2])

            # column C is entry (required)
            populate_entries(word, gramcats, row[3])

            # column E is example (optional)
            try:
                ex_str = row[5]
            except IndexError:
                continue
            populate_examples(word, ex_str)

            # column F is verb conjugation
            try:
                conjugation_str = row[6]
            except IndexError:
                continue
            populate_verbal_conjugation(word, gramcats, conjugation_str)

    def write_to_database():
        count_words = 0
        count_entries = 0
        count_examples = 0
        for _, word in cleaned_data.items():

            word.lexicon_id = lexicon_pk
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

        sys.stdout.write("Imported: %s words, %s entries, %s examples" %
                         (count_words, count_entries, count_examples))
        return count_words

    # check that GramaticalCategories are initialized
        if not GramaticalCategory.objects.all().exists():
            ii.status = ImportsInfo.FAILED
            ii.errors = ("There isn't any GramaticalCategory in the database. " +
                         "Gramatical Categories should be initialized before importing " +
                         "data for example running manage.py importgramcat.")
            ii.save()

            raise CommandError(
                "There isn't any GramaticalCategory in the database. "
                "Gramatical Categories should be initialized before importing "
                "data for example running manage.py importgramcat."
            )

    db = read_input_file()

    populate_models(db)

    if not dry_run:
        # Write data into the database
        try:
            count_words = write_to_database()
            ii.status = ImportsInfo.COMPLETED
            ii.num_rows = count_words
        except IntegrityError as e:
            ii.status = ImportsInfo.FAILED
            ii.errors = str(e)
            ii.save()
            raise CommandError("Error: " + e)

    if errors:
        ii.status = ImportsInfo.COMPLETED_WITH_ERRORS
        ii.errors = errors

    ii.save()

    return errors
