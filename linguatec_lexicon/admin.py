from django.contrib import admin

from . import models

@admin.register(models.Lexicon)
class LexiconAdmin(admin.ModelAdmin):
    list_display = ('name', 'src_language', 'dst_language',)
    search_fields = ('name',)
    list_filter = ('src_language', 'dst_language',)

@admin.register(models.GramaticalCategory)
class GramaticalCategoryAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'title',)
    
@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('term', 'lexicon',)
    search_fields = ('term',)
    list_filter = ('lexicon__name', 'lexicon__src_language', 'lexicon__dst_language',)


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'variation')
    search_fields = ('word__term',)
    list_filter = ('word__lexicon', 'word__lexicon__src_language', 'word__lexicon__dst_language',)
    
    # TODO show GramCats

@admin.register(models.Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'entry', )
    search_fields = ('entry__word__term',)
    list_filter = ('entry__word__lexicon', 'entry__word__lexicon__src_language', 'entry__word__lexicon__dst_language',)
