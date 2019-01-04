from django.test import TestCase


class FooTestCase(TestCase):
    """
    Just a fake test to prepare CI environment.
    TODO remove this class when valid tests are implemented.
    
    """

    def test_sum(self):
        self.assertEqual(2 + 2, 4)
