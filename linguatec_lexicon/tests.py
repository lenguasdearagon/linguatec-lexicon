import os
import unittest

from django.core.management import call_command
from django.test import TestCase
from linguatec_lexicon.models import Word

from .models import Lexicon, Word, Entry, Example


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
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/sample-input.xlsx')
        call_command('data-import', sample_path, dry_run=True)

        self.assertEqual(0, Word.objects.count())
        self.assertEqual(0, Entry.objects.count())
        self.assertEqual(0, Example.objects.count())