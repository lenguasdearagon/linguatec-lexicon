import os
import unittest

from django.core.management import call_command
from django.db import connection, IntegrityError
from django.test import TestCase

from linguatec_lexicon.models import (
    Entry, GramaticalCategory, Lexicon, VerbalConjugation, Word, Region, DiatopicVariation)


class GramCatTestCase(TestCase):
    def test_bug64_too_long_abbr(self):
        # This bug affects PostgreSQL and MySQL but not SQLite
        abbr = "pron. pers. tónico de 1ª pers. de sing."
        title = "pronombre personal tónico de primera persona del singular"
        gramcat = GramaticalCategory.objects.create(
            abbreviation=abbr, title=title)

        self.assertEqual(abbr, gramcat.abbreviation)


class MultipleGramCatsTestCase(TestCase):
    """
    Tests of issue #42 - add support to multiple gramatical categories

    """

    def setUp(self):
        ACCEPTED_GRAMCATS = [
            "adj.",
            "adv.",
            "part.",
            "s.",
            "v. prnl.",
            "v. tr.",
        ]
        self.lex = Lexicon.objects.create(
            name="lexicon", src_language="es", dst_language="ar")
        for abbr in ACCEPTED_GRAMCATS:
            GramaticalCategory.objects.create(abbreviation=abbr, title="-")

    def create_word(self, term):
        return Word.objects.create(lexicon=self.lex, term=term)

    def get_gramcat(self, abbr):
        return GramaticalCategory.objects.get(abbreviation=abbr)

    def test_word_one_gramcat_one_entry(self):
        w = self.create_word("lorem")
        g = self.get_gramcat("v. tr.")
        e = Entry.objects.create(
            word=w, translation="Aliquam tristique nulla vitae elit feugiat")
        e.gramcats.add(g)

    def test_word_one_gramcat_several_entries(self):
        w = self.create_word("sem")
        g = self.get_gramcat("v. prnl.")
        e = Entry.objects.create(
            word=w, translation="Nullam maximus vel ligula sed cursus.")
        e2 = Entry.objects.create(
            word=w, translation="Sed egestas eros non orci sodales.")
        e.gramcats.add(g)
        e2.gramcats.add(g)

    def test_word_several_gramcat_diferent_entries(self):
        w = self.create_word("feugiat")
        g = self.get_gramcat("adj.")
        e = Entry.objects.create(
            word=w, translation="Quisque nunc magna")
        e.gramcats.add(g)

        g2 = self.get_gramcat("adv.")
        e2 = Entry.objects.create(
            word=w, translation="eu tempor tellus accumsan")
        e2.gramcats.add(g2)

    def test_word_several_gramcat_sharing_entry(self):
        w = self.create_word("suscipit")
        g = self.get_gramcat("adj.")
        g2 = self.get_gramcat("s.")
        e = Entry.objects.create(word=w, translation="vestibulum")

        e.gramcats.add(g)
        e.gramcats.add(g2)

    def test_word_several_gramcat_sharing_several_entries(self):
        w = self.create_word("tristique")
        g = self.get_gramcat("part.")
        g2 = self.get_gramcat("adj.")
        e = Entry.objects.create(word=w, translation="porttitor")
        e2 = Entry.objects.create(word=w, translation="posuere")

        e.gramcats.add(g)
        e.gramcats.add(g2)
        e2.gramcats.add(g)
        e2.gramcats.add(g2)

    # TODO create tests for invalid combinations


class VerbalConjugationModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lexicon = Lexicon.objects.create(
            name='es-ar', src_language='es', dst_language='ar',
        )

    def setUp(self):
        # importdata requires that GramaticalCategories are initialized
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/verbal-conjugation.xlsx')
        call_command('importdata', self.lexicon.code, sample_path)

    def test_extract_verbal_conjugation(self):
        word = Word.objects.get(term="abarcar", lexicon=Lexicon.objects.get(src_language='es', dst_language='ar'))
        entry = word.entries.get(translation__contains="adubir")
        self.assertIsNotNone(entry.conjugation)

        parsed_conjugation = entry.conjugation.parse_raw
        self.assertIn("conjugation", parsed_conjugation)

    def test_extract_verbal_model(self):
        word = Word.objects.get(term="zambullir", lexicon=Lexicon.objects.get(src_language='es', dst_language='ar'))
        entry = word.entries.get(translation__contains="capuzar")
        parsed_conjugation = entry.conjugation.parse_raw
        self.assertIn("model", parsed_conjugation)
        self.assertIn("trobar", parsed_conjugation["model"])

    def test_extract_verbal_model_2(self):
        v = VerbalConjugation(raw='atrebuyir modelo. conjug. muyir (ordeñar)')
        parsed_conjugation = v.parse_raw
        self.assertIn("model", parsed_conjugation)
        self.assertIn("muyir", parsed_conjugation["model"])

    def test_extract_neither_conjugation_neither_model(self):
        v = VerbalConjugation(raw='Lorem ipsum.')
        parsed_conjugation = v.parse_raw
        self.assertIn("intro", parsed_conjugation)
        self.assertEqual(v.raw, parsed_conjugation["intro"])

    def test_partial_verbal_conjugation(self):
        """Related to issue #66"""
        value = """
        enzertar (irreg.) conjug. IND. pres. enzierto, enziertas...;
        SUBJ. pres. enzierte, enziertes…; IMP. enzierta, enzertaz;
        INF. enzertar; GER. enzertando; PART. enzertato/a.
        """
        value = value.replace("\n", "").strip()
        v = VerbalConjugation(raw=value)
        parsed_conjugation = v.parse_raw
        self.assertIn("intro", parsed_conjugation)
        self.assertEqual(v.raw, parsed_conjugation["intro"])


class WordManagerTestCase(TestCase):
    fixtures = ['lexicon-sample.json']

    def test_search_found(self):
        result = Word.objects.search("edad", "es-ar")
        self.assertEqual(1, result.count())

    def test_search_not_found(self):
        result = Word.objects.search("no sense word", "es-ar")
        self.assertEqual(0, result.count())

    def test_search_null_query(self):
        result = Word.objects.search(None, "es-ar")
        self.assertEqual(0, result.count())

    @unittest.skipUnless(connection.vendor == 'postgresql', "requires PostgreSQL backend")
    def test_search_sorted(self):
        Word.objects.bulk_create([
            Word(lexicon_id=1, term="hacer acopio"),
            Word(lexicon_id=1, term="hacer camino"),
            Word(lexicon_id=1, term="hacer"),
        ])
        result = Word.objects.search("hacer", "es-ar")
        self.assertEqual(result[0].term, "hacer")

    def test_search_query_unbalanced_parenthesis(self):
        result = Word.objects.search("largo(a", "es-ar")
        self.assertEqual(0, result.count())


class EntryModelTestCase(TestCase):

    @classmethod
    def get_fixture_path(cls, name):
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'fixtures/{}'.format(name))

    @classmethod
    def setUpTestData(cls):
        cls.lexicon = Lexicon.objects.create(
            name='es-ar', src_language='es', dst_language='ar',
        )

        cls.ribagorza = Region.objects.create(name="Ribagorza")

        # Create DiatopicVariation
        cls.variation = DiatopicVariation.objects.create(
            name="benasqués",
            abbreviation="Benas.",
            region=cls.ribagorza,
        )

    def setUp(cls):
        # importdata requires that GramaticalCategories are initialized
        sample_path = cls.get_fixture_path('gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

        # initialize words on main language
        sample_path = cls.get_fixture_path('variation-sample-common.xlsx')
        # import pdb; pdb.set_trace()
        call_command('importdata', cls.lexicon.name, sample_path)

        # import entries of benasqués variation
        sample_path = cls.get_fixture_path('variation-sample-benasques.xlsx')
        call_command('importvariation', cls.lexicon.code, sample_path, variation=cls.variation.name)

    def test_deny_importation_duplicated_entries(self):

        with self.assertRaises(IntegrityError):
            sample_path = self.get_fixture_path('variation-sample-benasques.xlsx')
            call_command('importvariation', self.lexicon.code, sample_path, variation=self.variation.name)
