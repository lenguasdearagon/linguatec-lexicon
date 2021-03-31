import os
import unittest

from django.test import TestCase

from linguatec_lexicon.models import Entry, Lexicon, GramaticalCategory


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
        
    def test_with_one_unique_word_case(self):
        # One entry without translation verb in the system
        self.assertTrue(not 'jugar' in self.result)

    def test_with_dash_in_aragonese_word(self):
        # One entry without translation verb in the system
        self.assertTrue('acochar-se' in self.result['agacharse'])

    def test_without_dash_in_aragonese_word(self):
        # One entry without translation verb in the system
        self.assertTrue(not 'reclochar-se' in self.result['agacharse'])
        self.assertTrue('reclochar' in self.result['agacharse'])

    def test_check_results(self):
        # checking that exist all possible results
        castellano = Lexicon.objects.get(src_language='es')
        kind_of_verbs = GramaticalCategory.get_abbr_verbs()
        entries = Entry.objects.filter(
            word__lexicon=castellano).filter(
                gramcats__abbreviation__in=kind_of_verbs).filter(
                    translation__contains=' ').distinct()

        bad_results = []
        for e in entries:
            if e.word.term not in self.result:
                bad_results.append(e.word.term)
        self.assertTrue(bad_results == [])
