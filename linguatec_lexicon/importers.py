import pandas as pd
import sys

from linguatec_lexicon.models import (Entry, GramaticalCategory, Word, Lexicon, DiatopicVariation)

from django.core.exceptions import ValidationError
from django.core.management.base import CommandError


def load_gramcats(csv_files):
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

    return loaded_object_count, csv_count


def import_variation(input_file, lexicon, variation, dry_run):

    errors = []

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
                raise ValidationError(message, code='B', params={'value': abbr})

        return gramcats

    def populate_entries(word, gramcats, translations_raw):
        word.clean_entries = []

        try:
            translations_list = translations_raw.split('//')
        except AttributeError:
            # e.g. empty cell is translated as float(nan)
            message = 'Word %(word)s contains empty or invalid translations.'
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

    # check that GramaticalCategories are initialized
    if not GramaticalCategory.objects.all().exists():
        raise CommandError(
            "There isn't any GramaticalCategory in the database. "
            "Gramatical Categories should be initialized before importing "
            "data for example running manage.py importgramcat."
        )

    xlsx = pd.read_excel(input_file, sheet_name=None, header=None, usecols="A:C",
                         names=['term', 'gramcats', 'translations'])
    cleaned_data = populate_models(xlsx)

    if not dry_run:
        write_to_database(cleaned_data)

    return errors, cleaned_data
