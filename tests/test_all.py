import os
import unittest
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from linguatec_lexicon.models import (DiatopicVariation, Entry, Example,
                                      GramaticalCategory, Lexicon, Region,
                                      VerbalConjugation, Word)


class ImporterTestCase(TestCase):
    def setUp(self):
        # importdata requires that GramaticalCategories are initialized
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

    def test_import_sample(self):
        """
        Input file:
        -----------
        fixtures/sample-input.xlsx

        Expected output exported on file: fixtures/sample-output.json running:
        ---------------------------------------------------------------------
        from django.core.management import call_command
        call_command('dumpdata', 'linguatec_lexicon', indent=4, output='sample-output.json')

        Side effects: creation of the objects into the database
        -----------------------------------------------

        """
        NUMBER_OF_WORDS = 12
        NUMBER_OF_ENTRIES = 16
        NUMBER_OF_EXAMPLES = 2

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/sample-input.xlsx')
        call_command('importdata', sample_path)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())
        self.assertEqual(NUMBER_OF_ENTRIES, Entry.objects.count())
        self.assertEqual(NUMBER_OF_EXAMPLES, Example.objects.count())

        # TODO make a more depth comparation between
        # call_command('dumpdata', 'linguatec_lexicon', indent=4, output='/tmp/test-output.json')
        # and fixtures/sample-output.json

    def test_missing_letters_as_sheets(self):
        NUMBER_OF_WORDS = 4

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/abcd.xlsx')
        call_command('importdata', sample_path)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())

    def test_dry_run(self):
        lexicon_initial = Lexicon.objects.count()

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/sample-input.xlsx')
        call_command('importdata', sample_path, dry_run=True)

        self.assertEqual(lexicon_initial, Lexicon.objects.count())
        self.assertEqual(0, Word.objects.count())
        self.assertEqual(0, Entry.objects.count())
        self.assertEqual(0, Example.objects.count())

    def test_invalid_gramcat_unkown(self):
        out = StringIO()
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/invalid-gramcat-unknown.xlsx')
        call_command('importdata', sample_path, stdout=out)

        # data shouldn't be imported if there are any errors
        self.assertEqual(0, Word.objects.count())
        self.assertIn('invalid', out.getvalue())

    def test_invalid_gramcat_empty(self):
        out = StringIO()
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/invalid-gramcat-empty.xlsx')
        call_command('importdata', sample_path, stdout=out)

        # data shouldn't be imported if there are any errors
        self.assertEqual(0, Word.objects.count())
        self.assertIn('empty', out.getvalue())

    def test_word_several_gramcats(self):
        NUMBER_OF_WORDS = 6
        NUMBER_OF_ENTRIES = 8

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/multiple-gramcats.xlsx')
        call_command('importdata', sample_path)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())
        self.assertEqual(NUMBER_OF_ENTRIES, Entry.objects.count())

    def test_word_with_verbal_conjugation(self):
        NUMBER_OF_WORDS = 2
        NUMBER_OF_CONJUGATIONS = 2

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/verbal-conjugation.xlsx')
        call_command('importdata', sample_path)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())
        self.assertEqual(NUMBER_OF_CONJUGATIONS,
                         VerbalConjugation.objects.count())

        # check that conjugation is related to proper entry
        word = Word.objects.get(term="abarcar")
        entry = word.entries.get(translation__contains="adubir")
        self.assertIsNotNone(entry.conjugation)

    def test_word_with_partial_verbal_conjugation(self):
        NUMBER_OF_WORDS = 3
        NUMBER_OF_CONJUGATIONS = 3

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/partial-verbal-conjugation.xlsx')
        call_command('importdata', sample_path, allow_partial=True)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())
        self.assertEqual(NUMBER_OF_CONJUGATIONS,
                         VerbalConjugation.objects.count())


class ImportGramCatTestCase(TestCase):
    NUMBER_OF_GRAMCATS = 72

    def test_import(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path)

        self.assertEqual(self.NUMBER_OF_GRAMCATS,
                         GramaticalCategory.objects.count())

    def test_purge_and_import(self):
        GramaticalCategory.objects.create(abbreviation="f.", title="foo")
        existing_gramcats = GramaticalCategory.objects.count()

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, purge=True)

        self.assertNotEqual(self.NUMBER_OF_GRAMCATS + existing_gramcats,
                            GramaticalCategory.objects.count())


class ImportVariationTestCase(TestCase):
    NUMBER_OF_ENTRIES = 115

    def setUp(self):
        # Create Regions
        ribagorza = Region.objects.create(name="Ribagorza")

        # Create DiatopicVariation
        DiatopicVariation.objects.create(
            name="benasqués",
            abbreviation="Benas.",
            region=ribagorza,
        )

        # initialize GramaticalCategories
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

        # initialize words on main language
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/variation-sample-common.xlsx')
        call_command('importdata', sample_path)

    def test_import(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/variation-sample-benasques.xlsx')
        call_command('importvariation', sample_path,
                     variation='benasqués', verbosity=4)

        qs = Entry.objects.filter(variation__isnull=False).values(
            'word__id').order_by('word__id').distinct('word__id')
        self.assertEqual(self.NUMBER_OF_ENTRIES, qs.count())
