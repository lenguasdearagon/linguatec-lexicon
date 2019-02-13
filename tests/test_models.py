from django.test import TestCase

from linguatec_lexicon.models import GramaticalCategory


class GramCatTestCase(TestCase):
    def test_bug64_too_long_abbr(self):
        # This bug affects PostgreSQL and MySQL but not SQLite
        abbr = "pron. pers. tónico de 1ª pers. de sing."
        title = "pronombre personal tónico de primera persona del singular"
        gramcat = GramaticalCategory.objects.create(abbreviation=abbr, title=title)
        
        self.assertEqual(abbr, gramcat.abbreviation)
