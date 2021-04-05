import os
import unittest

from django.test import TestCase

from linguatec_lexicon.models import Entry, Lexicon, GramaticalCategory, VerbalConjugation


class ConjugationTestCase(TestCase):

    fixtures = ['lexicons.json',
                'gramatical.json',
                'words.json',
                'entries.json',
                'entries_gramcats.json']

    def setUp(cls):
        cls.result = Entry.words_conjugation()

        for k_entry, v_raw in cls.result.items():
            for entry in Entry.objects.filter(word__term=k_entry):
                verbs = VerbalConjugation.objects.filter(entry=entry)
                if verbs:
                    verb = verbs.first()
                    verb.raw_verbs = v_raw
                    verb.save()
                else:
                    VerbalConjugation.objects.create(
                        entry=entry,
                        raw_verbs=v_raw
                    )

    def test_ideal_case(self):
        # unique word in the correspondence translation
        self.assertTrue('estraniar' in self.result['extrañar'])
        self.assertTrue('estrañar' in self.result['extrañar'])

    def test_without_representation_case(self):
        # One entry without translation verb in the system
        self.assertTrue(self.result['eclipsar'] == [])
        
    def test_with_one_unique_word_case(self):
        # One entry with only one word in translation
        self.assertTrue(not 'jugar' in self.result)

    def test_with_dash_in_aragonese_word(self):
        # One entry with dash in translation
        self.assertTrue('acochar-se' in self.result['agacharse'])

    def test_without_dash_in_aragonese_word(self):
        # One entry without dash in the verb than it is registred but with dash in translation
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

    def test_query_api(self):
        # check the result of query to api
        resp = self.client.get('/api/words/search/?q={}&l=es-ar'.format('extrañar'))
        self.assertEqual(200, resp.status_code)

        result = resp.json()
        verbs = result['results'][0]['entries'][0]['conjugation']['verbalraw']
        self.assertTrue('estraniar' in verbs)
        self.assertTrue('estrañar' in verbs)
