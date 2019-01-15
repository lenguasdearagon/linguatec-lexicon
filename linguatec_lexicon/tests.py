from django.test import TestCase


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
