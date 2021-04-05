from django.core.management import call_command
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
        call_command('verbalconjugation')

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
        verbs = result['results'][0]['entries'][0]['conjugation']['raw_verbs']
        self.assertTrue('estraniar' in verbs)
        self.assertTrue('estrañar' in verbs)

    def test_with_exclusive_words_of_translation(self):
        # check if the verbalconjugation have only words than appear in translation
        verbs = VerbalConjugation.objects.filter(entry__word__term='proveer')
        for v in verbs:
            self.assertTrue(v.raw_verbs != self.result['proveer'])
            for w in v.raw_verbs:
                self.assertTrue(w in v.entry.translation)

    def test_check_verbals_without_aragonese_lexicode(self):
        # check if the verbalconjugation have only words than appear in translation
        ar_verbs = VerbalConjugation.objects.filter(
            entry__word__lexicon__src_language='ar',
        )
        es_verbs = VerbalConjugation.objects.filter(entry__word__term='abancalar')
        self.assertTrue(es_verbs.count() == 1)
        self.assertTrue(ar_verbs.count() == 0)
        # import pdb; pdb.set_trace()
        verb = es_verbs.first()
        self.assertTrue(verb.raw_verbs == self.result['abancalar'])
