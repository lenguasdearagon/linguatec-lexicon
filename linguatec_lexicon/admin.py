from django.contrib import admin
from linguatec_lexicon.models import (Entry, Example, VerbalConjugation)
from . import models


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


@admin.register(models.Lexicon)
class LexiconAdmin(admin.ModelAdmin):
    list_display = ('name', 'src_language', 'dst_language',)
    search_fields = ('name',)
    list_filter = ('src_language', 'dst_language',)


@admin.register(models.GramaticalCategory)
class GramaticalCategoryAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'title',)


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0
    show_change_link = True


@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('term', 'lexicon',)
    search_fields = ('term',)
    list_filter = (('lexicon__name', custom_titled_filter('Lexicon name')),
                   'lexicon__src_language',
                   'lexicon__dst_language',)
    inlines = [
        EntryInline,
    ]


class ExampleInline(admin.TabularInline):
    model = Example
    extra = 0


class VerbalConjugationInline(admin.StackedInline):
    model = VerbalConjugation
    extra = 0


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'variation')
    search_fields = ('word__term',)
    list_filter = ('word__lexicon',
                   'word__lexicon__src_language',
                   'word__lexicon__dst_language',
                   ('variation__region__name', custom_titled_filter('Region')))

    inlines = [
        ExampleInline,
        VerbalConjugationInline,
    ]

    # TODO show GramCats


@admin.register(models.Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'entry',)
    search_fields = ('entry__word__term',)
    list_filter = (('entry__word__lexicon', custom_titled_filter('Lexicon name')),
                   'entry__word__lexicon__src_language',
                   'entry__word__lexicon__dst_language',)


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.DiatopicVariation)
class DiatopicVariationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.ImportsInfo)
class ImportsInfoAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'input_file',)
