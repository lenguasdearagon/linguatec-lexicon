import unittest

from django.db import connection
from django.test import TestCase


class ApiTestCase(TestCase):
    fixtures = ['lexicon-sample.json']

    def test_word_list(self):
        resp = self.client.get('/api/words/')
        self.assertEqual(200, resp.status_code)

    def test_word_show(self):
        resp = self.client.get('/api/words/1/')
        self.assertEqual(200, resp.status_code)

    def test_word_search_with_results(self):
        resp = self.client.get('/api/words/search/?q=echar&l=diccionario linguatec')
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertEqual(1, resp_json["count"])

    def test_word_search_no_results(self):
        resp = self.client.get('/api/words/search/?q=foo&l=diccionario linguatec')
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertEqual(0, resp_json["count"])


class GramaticalCategoryAPITestCase(TestCase):
    fixtures = ['gramcatical-categories.json']

    def test_gramcat_list(self):
        resp = self.client.get('/api/gramcats/')
        self.assertEqual(200, resp.status_code)

    def test_gramcat_show_by_id(self):
        resp = self.client.get('/api/gramcats/1/')
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertIn('abbreviation', resp_json)
        self.assertEqual('adj.', resp_json['abbreviation'])
        self.assertEqual('adjetivo', resp_json['title'])

    def test_gramcat_show_by_abbr(self):
        resp = self.client.get('/api/gramcats/show/?abbr=adj.')
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertIn('abbreviation', resp_json)
        self.assertEqual('adj.', resp_json['abbreviation'])
        self.assertEqual('adjetivo', resp_json['title'])


class VerbsAPITestCase(TestCase):
    fixtures = ['verbal-conjugation.json']

    def test_word_verb_is_conjugation_model(self):
        response = self.client.get('/api/words/8/').json()
        for entry in response['entries']:
            if 'adubir' in entry['translation']:
                self.assertIn('conjugation', entry['conjugation'])

    def test_word_verb_follows_regular_model(self):
        response = self.client.get('/api/words/8546/').json()
        for entry in response['entries']:
            if 'capuzar' in entry['translation']:
                self.assertIn('model', entry['conjugation'])
                self.assertIn('model_word_id', entry['conjugation'])
                self.assertEqual(entry['conjugation']['model_word_id'], 4434)


class SearchTestCase(TestCase):
    fixtures = ['lexicons.json',
                'gramcatical-categories.json', 'words-search.json']

    def do_and_check_query(self, query, expected_results):
        resp = self.client.get('/api/words/search/?q={}&l=diccionario linguatec'.format(query))
        self.assertEqual(200, resp.status_code)

        expected_results = set(expected_results)
        results = resp.json()["results"]
        results = set([x['term'] for x in results])

        self.assertSetEqual(expected_results, results)

    def test_exact_match(self):
        query = "garza"
        expected_results = ["garza"]
        self.do_and_check_query(query, expected_results)

    @unittest.skip("TODO desinence")
    def test_desincence_match(self):
        query = "enemistada"
        expected_results = ["enemistado/a"]
        self.do_and_check_query(query, expected_results)

    def test_expression_startswith(self):
        query = "espino"
        expected_results = ["espino", "espino blanco"]
        self.do_and_check_query(query, expected_results)

    def test_expression_startswith_two(self):
        query = "echar"
        expected_results = ["echar", "echar a", "echar a perder",
                            "echar a voleo", "echar de menos", "echar hojas"]
        self.do_and_check_query(query, expected_results)

    def test_expression_endswith(self):
        query = "atención"
        expected_results = ["atención", "prestar atención"]
        self.do_and_check_query(query, expected_results)

    @unittest.skip("TODO desinence")
    def test_desinence_expression(self):
        query = "añico"
        expected_results = ["añico", "hacerse añicos"]
        self.do_and_check_query(query, expected_results)

    @unittest.skip("TODO desinence")
    def test_desinence_expression_two(self):
        query = "bastar"
        expected_results = [
            "bastar", "bastarse por uno mismo", "bastarse para andar"]
        self.do_and_check_query(query, expected_results)

    def test_exclude_results(self):
        # word in query is contained but should be excluded
        query = "casa"
        expected_results = ["casa"]
        #should_be_excluded_in_terms = ["casar", "escasamente"]
        self.do_and_check_query(query, expected_results)


@unittest.skipUnless(connection.vendor == 'postgresql', "requires PostgreSQL backend")
class NearWordTestCase(TestCase):
    fixtures = ['lexicons.json',
                'gramcatical-categories.json', 'words-search.json']

    def test_no_results(self):
        query = "robot"
        resp = self.client.get('/api/words/near/?q={}'.format(query))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(0, resp.json()["count"])

    def test_typo(self):
        query = "batsar"
        resp = self.client.get('/api/words/near/?q={}'.format(query))
        self.assertEqual(200, resp.status_code)

        resp_json = resp.json()
        self.assertEqual(1, resp_json["count"])

        near_words = [x["term"] for x in resp_json["results"]]
        self.assertIn("bastar", near_words)
