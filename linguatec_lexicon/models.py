from django.db import models

from . import settings

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


# FIXME(@slamora) currently unused because search is implemented using
# django-rest-frameworks filters that provides a more powerfull search
# than using exact match.
class WordManager(models.Manager):
    def search(self, query):
        return self.filter(term=query)


class Word(models.Model):
    """
    The Word class stores each word (written in the source language)
    that compounds the Lexicon.

    """
    lexicon = models.ForeignKey('Lexicon', on_delete=models.CASCADE, related_name="words")
    term = models.CharField(unique=True, max_length=64)
    gramcat = models.CharField(max_length=32, choices=settings.GRAMATICAL_CATEGORIES)

    objects = WordManager()


class Entry(models.Model):
    """
    The Entry class represents each translation (written in the
    destination language) for a word (written in the source language).

    """
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name="entries")
    translation = models.TextField()


class Example(models.Model):
    """
    The Example class stores examples of usage of a Entry.

    """
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE, related_name="examples")
    phrase = models.TextField()