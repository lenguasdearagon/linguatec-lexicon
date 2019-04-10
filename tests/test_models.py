import os
import unittest

from django.core.management import call_command
from django.db import connection
from django.test import TestCase

from linguatec_lexicon.models import (
    Entry, GramaticalCategory, Lexicon, VerbalConjugation, Word)


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
    def setUp(self):
        # importdata requires that GramaticalCategories are initialized
        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(base_path, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

        base_path = os.path.dirname(os.path.abspath(__file__))
        sample_path = os.path.join(
            base_path, 'fixtures/verbal-conjugation.xlsx')
        call_command('importdata', sample_path)

    def test_extract_verbal_conjugation(self):
        word = Word.objects.get(term="abarcar")
        entry = word.entries.get(translation__contains="adubir")
        self.assertIsNotNone(entry.conjugation)

        parsed_conjugation = entry.conjugation.parse_raw
        self.assertIn("conjugation", parsed_conjugation)

    def test_extract_verbal_model(self):
        word = Word.objects.get(term="zambullir")
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
        result = Word.objects.search("edad")
        self.assertEqual(1, result.count())

    def test_search_not_found(self):
        result = Word.objects.search("no sense word")
        self.assertEqual(0, result.count())

    def test_search_null_query(self):
        result = Word.objects.search(None)
        self.assertEqual(0, result.count())

    @unittest.skipUnless(connection.vendor == 'postgresql', "requires PostgreSQL backend")
    def test_search_sorted(self):
        Word.objects.bulk_create([
            Word(lexicon_id=1, term="hacer acopio"),
            Word(lexicon_id=1, term="hacer camino"),
            Word(lexicon_id=1, term="hacer"),
        ])
        result = Word.objects.search("hacer")
        self.assertEqual(result[0].term, "hacer")
