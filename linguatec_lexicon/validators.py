import logging
import string

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)

# TODO move to settings or similar
logging.basicConfig(format='%(levelname)-8s {%(filename)s:%(lineno)d} [%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)


def validate_morfcat(value):
    # TODO reimplement when gramcat are stored in the DB
    from . import settings
    if value not in settings.GRAMATICAL_CATEGORIES:
        raise ValidationError(_('Enter a valid value.'))


@deconstructible
class VerbalConjugationValidator:
    # Verbal moods
    INDICATIVE = 'IND.'
    SUBJUNTIVE = 'SUBJ.'
    IMPERATIVE = 'IMP.'
    INFINITIVE = 'INF.'
    GERUND = 'GER.'
    PARTICIPLE = 'PART.'
    # Verbal tenses
    PRESENT = 'pres.'
    PAST_IMPERFECT = 'pret. imp.'
    PAST_INDEFINED = 'pret. indef.'
    FUTURE = 'fut.'
    CONDITIONAL = 'cond.'
    # Verbal moods and tenses must be in order
    MOODS = [INDICATIVE, SUBJUNTIVE, IMPERATIVE,
             INFINITIVE, GERUND, PARTICIPLE]
    MOOD_TENSES = {
        INDICATIVE: [PRESENT, PAST_IMPERFECT, PAST_INDEFINED, FUTURE, CONDITIONAL],
        SUBJUNTIVE: [PRESENT, PAST_IMPERFECT],
        IMPERATIVE: [''],
        INFINITIVE: [''],
        GERUND: [''],
        PARTICIPLE: [''],
    }
    MOOD_NUMBER_OF_CONJUGATIONS = {
        INDICATIVE: 6,
        SUBJUNTIVE: 6,
        IMPERATIVE: 2,
        INFINITIVE: 1,
        GERUND: 1,
        PARTICIPLE: 1,
    }
    message = _('Enter a valid verbal conjugation.')
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        # Validate that all the moods are present
        for mood in self.MOODS:
            if mood not in value:
                raise ValidationError(_('Verbal mood %s not found.') % mood)

        # Validate that conjugations are complete
        for mood in self.MOODS:
            mood_value = self.extract_mood(value, mood)
            for tense in self.MOOD_TENSES[mood]:
                count = self.MOOD_NUMBER_OF_CONJUGATIONS[mood]
                self.validate_number_of_conjugations(
                    mood_value, mood, tense, count)

    def extract_mood(self, value, mood):
        mood_idx = self.MOODS.index(mood)
        next_mood = self.MOODS[mood_idx + 1] if mood_idx + \
            1 < len(self.MOODS) else None
        beg = value.find(mood)
        end = value.find(next_mood) if next_mood is not None else None

        return value[beg:end].lstrip(mood).strip()

    def extract_tense(self, value, mood, tense):
        # TODO merge with extract_mood??
        mood_tenses = self.MOOD_TENSES[mood]
        tense_idx = mood_tenses.index(tense)
        next_tense = mood_tenses[tense_idx +
                                 1] if tense_idx + 1 < len(mood_tenses) else None
        beg = value.find(tense)
        end = value.find(next_tense) if next_tense is not None else None

        return value[beg:end].lstrip(tense).strip().rstrip(';')

    def extract_conjugation(self, value):
        stuff_chars = string.punctuation + string.whitespace
        conjugation = [x.strip(stuff_chars) for x in value.split(',')]
        return conjugation

    def validate_number_of_conjugations(self, value, mood, tense, count):
        value = self.extract_tense(value, mood, tense)
        conjugation = self.extract_conjugation(value)
        if len(conjugation) != count:
            raise ValidationError(
                _('Invalid number of conjugations for %s - %s. Should be %d' % (mood, tense, count)))
        logger.debug("%s %s: %s" % (mood, tense, conjugation))

        return True

    def __eq__(self, other):
        return isinstance(other, VerbalConjugationValidator)
