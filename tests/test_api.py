from django.test import TestCase


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
