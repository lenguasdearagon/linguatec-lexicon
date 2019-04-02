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
