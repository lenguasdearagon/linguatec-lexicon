from django.test import TestCase
from linguatec_lexicon.models import Word


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
