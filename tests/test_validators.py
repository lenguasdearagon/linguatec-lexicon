from django.core.exceptions import ValidationError
from django.test import TestCase

from linguatec_lexicon.validators import (
    validate_column_verb_conjugation, validate_verb_reference_to_model, VerbalConjugationValidator)


class ColumnFValidatorTestCase(TestCase):
    def test_verb_linking_conjugation_model(self):
        value = """
            Los verbos capuzar y zabucar son regulares de la
            1ª conjugación. modelo. conjug. trobar (hallar)
            """
        clean_data = validate_column_verb_conjugation(value)
        self.assertIn('model', clean_data)

    def test_verb_conjugation_model(self):
        value = """
            Es verbo regular de la 2ª conjugación. conjug. IND. pres. bebo,
            bebes, bebe, bebemos, bebez, beben; pret. imp. bebeba,
            bebebas, bebeba, bebébanos, bebébaz, bebeban; pret. indef. bebié,
            bebiés, bebió, bebiemos, bebiez, bebioron; fut. beberé, beberás,
            beberá, beberemos, beberez, beberán; cond. beberba, beberbas,
            beberba, bebérbanos, bebérbaz, beberban; SUBJ. pres. beba, bebas,
            beba, bebamos, bebaz, beban; pret. imp. bebese, bebeses,
            bebese, bebésenos, bebésez, bebesen; IMP. bebe, bebez; INF. beber;
            GER. bebendo. PART. bebito/a.
            """
        clean_data = validate_column_verb_conjugation(value)
        self.assertIn('conjugation', clean_data)

    def test_verb_conjugation_model2(self):
        value = """
            Verbo irregular. conjug. IND. pres. tiengo, tiens/tienes, tiene/tien,
            tenemos, tenez, tienen; pret. imp. teneba, tenebas, teneba, tenébanos,
            tenébaz, teneban; pret. indef. tenié/tuve, teniés/tuves, tenió/tuvo,
            teniemos /túvenos, teniez/túvez, tenioron/tuvon; fut. tendré, tendrás,
            tendrá, tendremos, tendrez, tendrán; cond. tenerba, tenerbas, tenerba,
            tenérbanos, tenérbaz, tenerban; SUBJ. pres. tienga, tiengas, tienga,
            tiengamos/tengamos, tiengaz / tengaz, tiengan; pret. imp. tenese,
            teneses, tenese, tenésenos, tenésez, tenesen; IMP. tiene, tenez; INF.
            tener; GER. tenendo; PART. tenito/a.
        """
        EXPECTED_RESULT = {
            'conjugation': {
                'IND.': {
                    'pres.': ['tiengo', 'tiens/tienes', 'tiene/tien', 'tenemos', 'tenez', 'tienen'],
                    'pret. imp.': ['teneba', 'tenebas', 'teneba', 'tenébanos', 'tenébaz', 'teneban'],
                    'pret. indef.': ['tenié/tuve', 'teniés/tuves', 'tenió/tuvo',
                                     'teniemos /túvenos', 'teniez/túvez', 'tenioron/tuvon'],
                    'fut.': ['tendré', 'tendrás', 'tendrá', 'tendremos', 'tendrez', 'tendrán'],
                    'cond.': ['tenerba', 'tenerbas', 'tenerba', 'tenérbanos', 'tenérbaz', 'tenerban']
                },
                'SUBJ.': {
                    'pres.': ['tienga', 'tiengas', 'tienga', 'tiengamos/tengamos', 'tiengaz / tengaz', 'tiengan'],
                    'pret. imp.': ['tenese', 'teneses', 'tenese', 'tenésenos', 'tenésez', 'tenesen']
                },
                'IMP.': {'': ['tiene', 'tenez']},
                'INF.': {'': ['tener']},
                'GER.': {'': ['tenendo']},
                'PART.': {'': ['tenito/a']}
            }
        }
        clean_data = validate_column_verb_conjugation(value)
        self.assertIn('conjugation', clean_data)
        self.assertDictEqual(clean_data, EXPECTED_RESULT)

    def test_extract_tense(self):
        conjugation_validator = VerbalConjugationValidator()
        value = """
        IND. pres. tiengo, tiens/tienes, tiene/tien,
            tenemos, tenez, tienen; pret. imp. teneba, tenebas, teneba, tenébanos,
            tenébaz, teneban; pret. indef. tenié/tuve, teniés/tuves, tenió/tuvo,
            teniemos /túvenos, teniez/túvez, tenioron/tuvon; fut. tendré, tendrás,
            tendrá, tendremos, tendrez, tendrán; cond. tenerba, tenerbas, tenerba,
            tenérbanos, tenérbaz, tenerban;
        """
        EXPECTED_RESULT = ["teneba", "tenebas", "teneba", "tenébanos", "tenébaz", "teneban"]
        mood = conjugation_validator.INDICATIVE
        tense = conjugation_validator.PAST_IMPERFECT
        tense_content = conjugation_validator.extract_tense(value, mood, tense)
        result = conjugation_validator.extract_conjugation(tense_content)
        self.assertEqual(result, EXPECTED_RESULT)

    def test_mood_and_tenses_keep_order(self):
        value = """
            conjug. IND. pres. tiengo, tiens/tienes, tiene/tien,
            tenemos, tenez, tienen; pret. imp. teneba, tenebas, teneba, tenébanos,
            tenébaz, teneban; pret. indef. tenié/tuve, teniés/tuves, tenió/tuvo,
            teniemos /túvenos, teniez/túvez, tenioron/tuvon; fut. tendré, tendrás,
            tendrá, tendremos, tendrez, tendrán; cond. tenerba, tenerbas, tenerba,
            tenérbanos, tenérbaz, tenerban; SUBJ. pres. tienga, tiengas, tienga,
            tiengamos/tengamos, tiengaz / tengaz, tiengan; pret. imp. tenese,
            teneses, tenese, tenésenos, tenésez, tenesen; IMP. tiene, tenez; INF.
            tener; GER. tenendo; PART. tenito/a.
        """
        conjugation_validator = VerbalConjugationValidator()

        clean_data = validate_column_verb_conjugation(value)
        conjugation = clean_data["conjugation"]
        self.assertEqual(list(conjugation.keys()), conjugation_validator.MOODS)

        for mood in conjugation_validator.MOODS:
            tenses = conjugation[mood]
            self.assertEqual(list(tenses.keys()), conjugation_validator.MOOD_TENSES[mood])


class VerbReferenceToModel(TestCase):
    def test_valid(self):
        VALUES = [
            "trobar (hallar)",
            "trobar(hallar)",
            "trobar    (hallar)",
        ]
        EXPECTED_RESULT = ('trobar', 'hallar')
        for value in VALUES:
            result = validate_verb_reference_to_model(value)
            self.assertEqual(EXPECTED_RESULT, result)

    def test_error_missing_word(self):
        value = "trobar"
        self.assertRaises(ValidationError, validate_verb_reference_to_model, value)

    def test_error_unexpected_format(self):
        VALUES = [
            "trobar (hallar",
            "trobar hallar",
            "trobar hallar)",
            "(hallar)",
        ]
        for value in VALUES:
            self.assertRaises(ValidationError, validate_verb_reference_to_model, value)

    def test_bug_both_keywords(self):
        value = """
        acazegar (irregular) conjug.
        IND. pres. acaziego, acaziegas, acaziega, acazegamos, acazegaz, acaziegan;
        SUBJ. pres. acaziegue, acaziegues, acaziegue, acazeguemos, acazeguez, acazieguen;
        IMP. acaziega, acazegaz; INF. acazegar; GER. acazegando;
        PART. acazegato/a-acazegau/acazegada.
        El resto de los tiempos es regular. modelo. conjug. trobar (encontrar)
        """
        clean_data = validate_column_verb_conjugation(value)
        self.assertIn('model', clean_data)
        self.assertIn('model_word', clean_data)

    def test_valid_reference_with_multiple_words(self):
        value = "modelo. conjug. caler (ser necesario)"
        clean_data = validate_column_verb_conjugation(value)
        self.assertIn('model', clean_data)
        self.assertIn('model_word', clean_data)


class VerbalConjugationValidatorTestCase(TestCase):
    INPUT = """
            Adubir es modelo para la conjugación regular
            de los verbos regulares terminados en –IR.
            conjug. IND. pres. adubo, adubes, adube,
            adubimos, adubiz, aduben; pret. imp.
            adubiba, adubibas, adubiba, adubíbanos,
            adubíbaz, adubiban; pret. indef. adubié,
            adubiés, adubió, adubiemos, adubiez,
            adubioron/adubión; fut. adubiré, adubirás,
            adubirá, adubiremos, adubirez, adubirán;
            cond. adubirba, adubirbas, adubirba,
            adubírbanos, adubírbaz, adubirban; SUBJ.
            pres. aduba, adubas, aduba, adubamos,
            adubaz, aduban; pret. imp. adubise,
            adubises, adubise, adubísenos, adubísez,
            adubisen; IMP. adube, adubiz; INF. adubir;
            GER. adubindo; PART. adubito/a.
            """
    INPUT2 = """
            Adubir es modelo para la conjugación regular
            de los verbos regulares terminados en –IR.
            conjug. IND. pres. adubo, adubes, adube,
            adubimos, adubiz, aduben; pret. imp.
            adubiba, adubibas, adubiba, adubíbanos,
            adubíbaz, adubiban; pret. indef. adubié,
            adubiés, adubió, adubiemos, adubiez,
            adubioron/adubión; fut. adubiré, adubirás,
            adubirá, adubiremos, adubirez, adubirán;
            cond. adubirba, adubirbas, adubirba,
            adubírbanos, adubírbaz, adubirban; SUBJ.
            pres. aduba, adubas, aduba, adubamos,
            adubaz, aduban; pret. imp. adubise,
            adubises, adubise, adubísenos, adubísez,
            adubisen; IMP. adube, adubiz; INF. adubir;
            GER. adubindo;
            """
    INPUT3 = """
            Adubir es modelo para la conjugación regular
            de los verbos regulares terminados en –IR.
            conjug. IND. pres. adubes, adube,
            adubimos, adubiz, aduben; pret. imp.
            adubiba, adubibas, adubiba, adubíbanos,
            adubíbaz, adubiban; pret. indef. adubié,
            adubiés, adubió, adubiemos, adubiez,
            adubioron/adubión; fut. adubiré, adubirás,
            adubirá, adubiremos, adubirez, adubirán;
            cond. adubirba, adubirbas, adubirba,
            adubírbanos, adubírbaz, adubirban; SUBJ.
            pres. aduba, adubas, aduba, adubamos,
            adubaz, aduban; pret. imp. adubise,
            adubises, adubise, adubísenos, adubísez,
            adubisen; IMP. adube, adubiz; INF. adubir;
            GER. adubindo; PART. adubito/a.
            """

    def test_valid_input(self):
        value = self.INPUT
        verbal_validator = VerbalConjugationValidator()
        verbal_validator(value)

    def test_invalid_input_missing_participle_mood(self):
        value = self.INPUT2
        verbal_validator = VerbalConjugationValidator()
        self.assertRaises(ValidationError, verbal_validator, value)

    def test_invalid_input_incomplete_infinitive_present_conjugation(self):
        value = self.INPUT3
        verbal_validator = VerbalConjugationValidator()
        self.assertRaises(ValidationError, verbal_validator, value)
