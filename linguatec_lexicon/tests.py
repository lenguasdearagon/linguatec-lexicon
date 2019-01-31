import os
import unittest

from django.core.management import call_command
from django.test import TestCase
from linguatec_lexicon.models import Word

from .models import Entry, Example, GramaticalCategory, Lexicon, Word


class FooTestCase(TestCase):
    """
    Just a fake test to prepare CI environment.
    TODO remove this class when valid tests are implemented.

    """

    def test_sum(self):
        self.assertEqual(2 + 2, 4)


class ApiTestCase(TestCase):
    fixtures = ['lexicon-sample.json']

    def test_word_list(self):
        resp = self.client.get('/api/words/')
        self.assertEqual(200, resp.status_code)

    def test_word_show(self):
        resp = self.client.get('/api/words/1/')
        self.assertEqual(200, resp.status_code)

    def test_word_search_several_results(self):
        resp = self.client.get('/api/words/?search=e')
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertEqual(4, len(resp_json))

    def test_word_search_no_results(self):
        resp = self.client.get('/api/words/?search=foo')
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertEqual(0, len(resp_json))


class WordManagerTestCase(TestCase):
    fixtures = ['lexicon-sample.json']

    def test_search_found(self):
        result = Word.objects.search("edad")
        self.assertEqual(1, result.count())

    def test_search_not_found(self):
        result = Word.objects.search("no sense word")
        self.assertEqual(0, result.count())

    def test_search_null_query(self):
        result = Word.objects.search(None)
        self.assertEqual(0, result.count())


class ImporterTestCase(TestCase):
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
        call_command('data-import', sample_path)

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
        call_command('data-import', sample_path)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())

    def test_dry_run(self):
        lexicon_initial = Lexicon.objects.count()

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/sample-input.xlsx')
        call_command('data-import', sample_path, dry_run=True)

        self.assertEqual(lexicon_initial, Lexicon.objects.count())
        self.assertEqual(0, Word.objects.count())
        self.assertEqual(0, Entry.objects.count())
        self.assertEqual(0, Example.objects.count())

    def test_word_several_gramcats(self):
        NUMBER_OF_WORDS = 6
        NUMBER_OF_ENTRIES = 8

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/multiple-gramcats.xlsx')
        call_command('data-import', sample_path)

        self.assertEqual(NUMBER_OF_WORDS, Word.objects.count())
        self.assertEqual(NUMBER_OF_ENTRIES, Entry.objects.count())


class ImportGramCatTestCase(TestCase):
    def test_import(self):
        NUMBER_OF_GRAMCATS = 21
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path)

        self.assertEqual(NUMBER_OF_GRAMCATS,
                         GramaticalCategory.objects.count())


class MultipleGramCatsTestCase(TestCase):
    """
    Tests of issue #42 - add support to multiple gramatical categories

    """

    def setUp(self):
        ACCEPTED_GRAMCATS = [
            "adj.",
            "adv.",
            "part.",
            "s.",
            "v. prnl.",
            "v. tr.",
        ]
        self.lex = Lexicon.objects.create(
            name="lexicon", src_language="es", dst_language="ar")
        for abbr in ACCEPTED_GRAMCATS:
            GramaticalCategory.objects.create(abbreviation=abbr, title="-")

    def create_word(self, term):
        return Word.objects.create(lexicon=self.lex, term=term)

    def get_gramcat(self, abbr):
        return GramaticalCategory.objects.get(abbreviation=abbr)

    def test_word_one_gramcat_one_entry(self):
        w = self.create_word("lorem")
        g = self.get_gramcat("v. tr.")
        e = Entry.objects.create(
            word=w, translation="Aliquam tristique nulla vitae elit feugiat")
        e.gramcats.add(g)

    def test_word_one_gramcat_several_entries(self):
        w = self.create_word("sem")
        g = self.get_gramcat("v. prnl.")
        e = Entry.objects.create(word=w, translation="Nullam maximus vel ligula sed cursus.")
        e2 = Entry.objects.create(word=w, translation="Sed egestas eros non orci sodales.")
        e.gramcats.add(g)
        e2.gramcats.add(g)

    def test_word_several_gramcat_diferent_entries(self):
        w = self.create_word("feugiat")
        g = self.get_gramcat("adj.")
        e = Entry.objects.create(
            word=w, translation="Quisque nunc magna")
        e.gramcats.add(g)

        g2 = self.get_gramcat("adv.")
        e2 = Entry.objects.create(
            word=w, translation="eu tempor tellus accumsan")
        e2.gramcats.add(g2)

    def test_word_several_gramcat_sharing_entry(self):
        w = self.create_word("suscipit")
        g = self.get_gramcat("adj.")
        g2 = self.get_gramcat("s.")
        e = Entry.objects.create(word=w, translation="vestibulum")

        e.gramcats.add(g)
        e.gramcats.add(g2)

    def test_word_several_gramcat_sharing_several_entries(self):
        w = self.create_word("tristique")
        g = self.get_gramcat("part.")
        g2 = self.get_gramcat("adj.")
        e = Entry.objects.create(word=w, translation="porttitor")
        e2 = Entry.objects.create(word=w, translation="posuere")

        e.gramcats.add(g)
        e.gramcats.add(g2)
        e2.gramcats.add(g)
        e2.gramcats.add(g2)

    # TODO create tests for invalid combinations
