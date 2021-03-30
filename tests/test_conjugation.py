import os
import unittest

from django.test import TestCase

from linguatec_lexicon.models import (
    Entry, GramaticalCategory, Lexicon, VerbalConjugation, Word)


class ConjugationTestCase(TestCase):

    fixtures = ['lexicons.json',
                'gramatical.json',
                'words.json',
                'entries.json',
                'entries_gramcats.json']

    def test_ideal_case(self):
        # unique word in the correspondence translation
        csv = 'echar;\nechar;\nechar;\nechar;\neclipsar;\n'
        self.assertTrue(csv in Entry.words_conjugation())
