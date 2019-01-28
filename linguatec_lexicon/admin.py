from django.contrib import admin

from . import models

@admin.register(models.Lexicon)
class LexiconAdmin(admin.ModelAdmin):
    list_display = ('name', 'src_language', 'dst_language',)

@admin.register(models.GramaticalCategory)
class GramaticalCategoryAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'title',)

@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('term', 'gramcat', 'lexicon',)

@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('translation', 'word',)

@admin.register(models.Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'entry',)
