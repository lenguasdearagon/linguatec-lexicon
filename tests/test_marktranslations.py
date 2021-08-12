import re

from django.test import TestCase
from linguatec_lexicon.management.commands import marktranslations

REGEX = marktranslations.Command.regex


class MarkTranslationRegex(TestCase):
    def assertRegexpFindAll(self, text, expected):
        matches = re.findall(REGEX, text)
        self.assertListEqual(expected, matches)

    def test_single_word(self):
        self.assertRegexpFindAll('casa', ['casa'])

    def test_several_words_comma_separated(self):
        self.assertRegexpFindAll('zerpeta, boira seca', ['zerpeta', 'boira', 'seca'])

    def test_words_with_dash(self):
        self.assertRegexpFindAll('pentinar-se', ['pentinar-se'])

    def test_words_with_slash(self):
        self.assertRegexpFindAll('casto/a', ['casto/a'])

    def test_exclude_words_surrounded_by_parenthesis(self):
        self.assertRegexpFindAll('(cúmulo) boira grasa', ['boira', 'grasa'])

    def test_exclude_words_surrounded_by_parenthesis_and_commas(self):
        self.assertRegexpFindAll(
            'boira (Puede emplearse con cuantificadores: dos boiras, bellas boiras, muitas boiras)',
            ['boira']
        )
