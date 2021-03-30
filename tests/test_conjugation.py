import os
import unittest

from django.test import TestCase

from linguatec_lexicon.models import Entry


class ConjugationTestCase(TestCase):

    fixtures = ['lexicons.json',
                'gramatical.json',
                'words.json',
                'entries.json',
                'entries_gramcats.json']

    def setUp(cls):
        cls.result = Entry.words_conjugation()

    def test_ideal_case(self):
        # unique word in the correspondence translation
        self.assertTrue('estraniar' in self.result['extrañar'])
        self.assertTrue('estrañar' in self.result['extrañar'])

    def test_without_representation_case(self):
        # One entry without translation verb in the system
        self.assertTrue(self.result['eclipsar'] == '')
