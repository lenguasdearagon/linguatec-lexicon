import re
import unittest

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from linguatec_lexicon.management.commands import marktranslations
from linguatec_lexicon.models import Entry, Lexicon, Word

REGEX = marktranslations.Command.regex


class MarkTextTest(TestCase):
    def test_a(self):
        Lexicon.objects.bulk_create([
            Lexicon(name="es-ar", src_language="es", dst_language="ar"),
            Lexicon(name="ar-es", src_language="ar", dst_language="es"),
        ])
        es = Lexicon.objects.get(name="es-ar")
        ar = Lexicon.objects.get(name="ar-es")

        Word.objects.bulk_create([
            Word(lexicon=es, term="prieto/a"),
            Word(lexicon=es, term="tirante"),
            Word(lexicon=ar, term="preto/a"),
        ])

        word = Word.objects.get(term="preto/a")
        entry = word.entries.create(translation="prieto/a, apretado/a, tirante")

        call_command('marktranslations')

        self.assertEqual(2, len(re.findall("</trans>", entry.marked_translation)))
        self.assertEqual(1, Entry.objects.exclude(marked_translation='').count())


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


class SplitByParenthesisTest(TestCase):
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
