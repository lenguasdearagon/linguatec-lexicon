import re
import unittest
from django.core.exceptions import ValidationError

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

    @unittest.expectedFailure
    def test_exclude_words_surrounded_by_parenthesis_and_commas(self):
        self.assertRegexpFindAll(
            'boira (Puede emplearse con cuantificadores: dos boiras, bellas boiras, muitas boiras)',
            ['boira']
        )


class MarkTranslationMethod(TestCase):
    def assertMethodSplit(self, text, expected):
        result = marktranslations.split_by_parenthesis(text)
        self.assertListEqual(expected, result)

    def test_single_word(self):
        self.assertMethodSplit('casa', ['casa'])

    def test_several_words_comma_separated(self):
        self.assertMethodSplit('zerpeta, boira seca', ['zerpeta, boira seca'])

    def test_words_with_dash(self):
        self.assertMethodSplit('pentinar-se', ['pentinar-se'])

    def test_words_with_slash(self):
        self.assertMethodSplit('casto/a', ['casto/a'])

    def test_exclude_words_surrounded_by_parenthesis(self):
        self.assertMethodSplit('(cúmulo) boira grasa', ['(cúmulo)', ' boira grasa'])

    def test_exclude_words_surrounded_by_parenthesis_and_commas(self):
        self.assertMethodSplit(
            'boira (Puede emplearse con cuantificadores: dos boiras, bellas boiras, muitas boiras) caraca, (has)',
            ['boira ', '(Puede emplearse con cuantificadores: dos boiras, bellas boiras, muitas boiras)',
             ' caraca, ', '(has)']
        )

    def test_invalid_unbalanced_parenthesis(self):
        self.assertRaises(ValidationError, marktranslations.split_by_parenthesis, '(')
