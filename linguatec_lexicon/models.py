from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models import Q
from django.utils.functional import cached_property

from linguatec_lexicon import validators


class Lexicon(models.Model):
    """
    The Lexicon class provides a class to define a bilingual dictionary.

    Keep in mind that you define the Lexicon direction choosing the
    source and destination language. This direction is not
    bidirectional, so if you want to have a complete bilingual dictionary
    you have to create two Lexicon, one for each way.

    For example, a lexicon with Spanish as source language and
    Aragonese as destination language stores the translation in Aragonese
    for a collection of words in Spanish.

    """
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    # TODO use ISO 639 codes??? https://www.iso.org/iso-639-language-codes.html
    src_language = models.CharField(max_length=16)
    dst_language = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class WordManager(models.Manager):
    def search(self, query):
        MIN_SIMILARITY = 0.3
        if connection.vendor == 'postgresql':
            iregex = r"\y{0}\y"
        elif connection.vendor == 'sqlite':
            iregex=r"\b{0}\b"
            return self.filter(term__iregex=iregex.format(query))
        else:
            filter_query = (
                Q(term=query) |
                Q(term__startswith=query) |
                Q(term__endswith=query)
            )
            return self.filter(filter_query)


        # sort results by trigram similarity
        qs = self.filter(
                term__iregex=iregex.format(query)
            ).annotate(similarity=TrigramSimilarity('term', query)
            ).filter(similarity__gt=MIN_SIMILARITY).order_by('-similarity')
        return qs

    def search_near(self, query):
        # https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/search/#trigram-similarity
        # https://www.postgresql.org/docs/current/pgtrgm.html
        # TODO which is the limit of similarity:
        # 0 means totally different
        # 1 means identical
        MIN_SIMILARITY = 0.2
        qs = self.annotate(
            similarity=TrigramSimilarity('term', query),
        ).filter(similarity__gt=MIN_SIMILARITY).order_by('-similarity')

        return qs


class Word(models.Model):
    """
    The Word class stores each word (written in the source language)
    that compounds the Lexicon.

    """
    lexicon = models.ForeignKey('Lexicon', on_delete=models.CASCADE, related_name="words")
    term = models.CharField(unique=True, max_length=64)

    objects = WordManager()

    def __str__(self):
        return self.term

    def gramcats(self):
        return self.entries.values_list('gramcats__abbreviation', flat=True).distinct()


class Entry(models.Model):
    """
    The Entry class represents each translation (written in the
    destination language) for a word (written in the source language).

    """
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name="entries")
    gramcats = models.ManyToManyField('GramaticalCategory', related_name="entries")
    translation = models.TextField()

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        return self.translation


class Example(models.Model):
    """
    The Example class stores examples of usage of a Entry.

    """
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE, related_name="examples")
    phrase = models.TextField()

    def __str__(self):
        return self.phrase


class GramaticalCategory(models.Model):
    abbreviation = models.CharField(unique=True, max_length=64)
    title = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "gramatical categories"

    def __str__(self):
        return self.abbreviation


class VerbalConjugation(models.Model):
    KEYWORD_MODEL = "modelo. conjug."
    KEYWORD_CONJUGATION = "conjug."

    entry = models.OneToOneField('Entry', on_delete=models.CASCADE, related_name="conjugation")
    raw = models.TextField('Raw imported content.')

    @cached_property
    def parse_raw(self):
        beg = None
        parsed = {}
        raw_lowcase = self.raw.lower()
        if self.KEYWORD_MODEL in raw_lowcase:
            beg = raw_lowcase.find(self.KEYWORD_MODEL)
            model_raw = raw_lowcase.split(self.KEYWORD_MODEL)[1].strip()
            model_parsed = validators.validate_verb_reference_to_model(model_raw)
            parsed["model"], parsed["model_word"] = model_parsed

        elif self.KEYWORD_CONJUGATION in raw_lowcase:
            beg = raw_lowcase.find(self.KEYWORD_CONJUGATION)
            # wordaround to allow partial conjugations see #66
            try:
                conjugation = validators.VerbalConjugationValidator()(self.raw)
            except ValidationError:
                beg = None
            else:
                parsed["conjugation"] = conjugation

        parsed["intro"] = self.raw[:beg].strip()

        return parsed

    @property
    def intro(self):
        return self.parse_raw.get('intro', None)

    @property
    def conjugation(self):
        return self.parse_raw.get('conjugation', None)

    @property
    def model(self):
        return self.parse_raw.get('model', None)

    @property
    def model_word(self):
        return self.parse_raw.get('model_word', None)

    @property
    def model_word_id(self):
        if self.model_word is None:
            return None
        try:
            return Word.objects.get(term=self.model_word).pk
        except Word.DoesNotExist:
            # TODO log this error to detect database inconsistency
            return None
