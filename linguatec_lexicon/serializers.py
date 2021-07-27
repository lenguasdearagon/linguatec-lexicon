import re
from rest_framework import serializers

from .models import (DiatopicVariation, Entry, Example, GramaticalCategory,
                     VerbalConjugation, Word, Lexicon)


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ('phrase',)


class VerbalConjugationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerbalConjugation
        fields = ('intro', 'model', 'model_word',
                  'model_word_id', 'conjugation')


class GramaticalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GramaticalCategory
        fields = ('abbreviation', 'title')


class DiatopicVariationSerializer(serializers.ModelSerializer):
    region = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = DiatopicVariation
        fields = ('name', 'abbreviation', 'region')


class EntrySerializer(serializers.ModelSerializer):
    gramcats = GramaticalCategorySerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)
    conjugation = VerbalConjugationSerializer()
    variation = DiatopicVariationSerializer()
    translation = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ('id', 'variation', 'gramcats', 'translation',
                  'examples', 'conjugation')

    def get_translation(self, obj):
        self.obj = obj
        translation = re.sub(r'(\w+)', self.mark_word, obj.translation)

        return translation

    def mark_word(self, matchobj):
        lex = self.obj.word.lexicon
        translation_exists = Word.objects.filter(term=matchobj.group(1)).exclude(lexicon=lex).exists()
        if translation_exists:
            lex_code = lex.dst_language + '-' + lex.src_language
            return "<trans lex=" + lex_code + ">" + matchobj.group(1) + "</trans>"
        else:
            return matchobj.group(1)


class WordSerializer(serializers.ModelSerializer):
    lexicon = serializers.SlugRelatedField(slug_field='code', read_only=True)
    entries = EntrySerializer(many=True, read_only=True)
    gramcats = serializers.ListField(read_only=True)

    class Meta:
        model = Word
        fields = ('url', 'lexicon', 'term', 'gramcats', 'entries', 'admin_panel_url')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        if not (user.is_authenticated and user.is_staff):
            self.fields.pop('admin_panel_url')


class WordNearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ('url', 'id', 'term')


class LexiconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lexicon
        fields = ('id', 'code', 'name', 'src_language', 'dst_language')
