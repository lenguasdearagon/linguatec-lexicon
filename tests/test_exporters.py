import os
import tempfile
from django.core.management import call_command
from django.test import TestCase

from linguatec_lexicon.models import (DiatopicVariation, Lexicon, Region)


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
APP_BASE_PATH = os.path.join(os.path.dirname(BASE_PATH), 'linguatec_lexicon')


class ExporterDataTestCase(TestCase):
    LEXICON_NAME = 'es-ar'
    LEXICON_CODE = 'es-ar'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Lexicon.objects.create(
            name=cls.LEXICON_NAME, src_language='es', dst_language='ar',
        )

    def setUp(self):
        # importdata requires that GramaticalCategories are initialized
        sample_path = os.path.join(APP_BASE_PATH, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

    def test_export_data(self):
        sample_path = os.path.join(BASE_PATH, 'fixtures/sample-input.xlsx')
        call_command('importdata', self.LEXICON_NAME, sample_path)

        with tempfile.TemporaryDirectory() as tmpdirname:
            output_path = os.path.join(tmpdirname, 'test-output-data-file.csv')
            call_command('exportdata', self.LEXICON_CODE, output_path)

            with open(output_path) as file:
                exported_content = file.read()

            expected_path = os.path.join(BASE_PATH, 'fixtures/export_test_files/export_data_expected_result.csv')
            with open(expected_path) as file:
                expected_content = file.read()

            self.assertListEqual(list(exported_content), list(expected_content))


class ExporterVariationTestCase(TestCase):

    LEXICON_CODE = 'es-ar'

    @classmethod
    def get_fixture_path(cls, name):
        return os.path.join(BASE_PATH, 'fixtures/{}'.format(name))

    @classmethod
    def setUpTestData(cls):
        lexicon = Lexicon.objects.create(
            name='es-ar', src_language='es', dst_language='ar',
        )

        # Create Regions
        ribagorza = Region.objects.create(name="Ribagorza")

        # Create DiatopicVariation
        DiatopicVariation.objects.create(
            name="benasqués",
            abbreviation="Benas.",
            region=ribagorza,
        )

        # initialize GramaticalCategories
        sample_path = os.path.join(APP_BASE_PATH, 'fixtures/gramcat-es-ar.csv')
        call_command('importgramcat', sample_path, verbosity=0)

        # initialize words on main language
        sample_path = cls.get_fixture_path('variation-sample-common.xlsx')
        call_command('importdata', lexicon.name, sample_path)

    def test_export_variation(self):
        sample_path = os.path.join(BASE_PATH, 'fixtures/variation-sample-benasques.xlsx')
        call_command('importvariation', self.LEXICON_CODE, sample_path, variation='benasqués')

        with tempfile.TemporaryDirectory() as tmpdirname:
            output_path = os.path.join(tmpdirname, 'test-output-data-file.csv')
            call_command('exportvariation', self.LEXICON_CODE, 'benasqués', output_path)

            with open(output_path) as file:
                exported_content = file.read()

            expected_path = os.path.join(BASE_PATH, 'fixtures/export_test_files/export_variation_expected_result.csv')
            with open(expected_path) as file:
                expected_content = file.read()

            self.assertListEqual(list(exported_content), list(expected_content))
