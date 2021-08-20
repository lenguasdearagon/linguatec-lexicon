from django.test import TestCase
from linguatec_lexicon import utils


class UtilsTest(TestCase):
    def test_lng_codes_iso_639_1(self):
        src, dst = utils.get_lexicon_languages_from_code("en-fr")
        self.assertEqual("en", src)
        self.assertEqual("fr", dst)

    def test_lng_codes_iso_639_2(self):
        src, dst = utils.get_lexicon_languages_from_code("arg-spa")
        self.assertEqual("arg", src)
        self.assertEqual("spa", dst)

    def test_invalid_code_format(self):
        self.assertRaises(ValueError, utils.get_lexicon_languages_from_code, "foo")

    def test_invalid_missing_dest_language_code(self):
        self.assertRaises(ValueError, utils.get_lexicon_languages_from_code, "foo-")
