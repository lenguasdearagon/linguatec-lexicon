from rest_framework import serializers

from .models import Entry, Example, GramaticalCategory, VerbalConjugation, Word


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ('phrase',)


class VerbalConjugationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerbalConjugation
        fields = ('intro', 'model', 'model_word', 'model_word_id', 'conjugation')


class EntrySerializer(serializers.ModelSerializer):
    examples = ExampleSerializer(many=True, read_only=True)
    conjugation = VerbalConjugationSerializer()

    class Meta:
        model = Entry
        fields = ('translation', 'examples', 'conjugation')


class WordSerializer(serializers.ModelSerializer):
    entries = EntrySerializer(many=True, read_only=True)
    gramcats = serializers.ListField(read_only=True)

    class Meta:
        model = Word
        fields = ('url', 'term', 'gramcats', 'entries')


class WordNearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ('url', 'id', 'term')


class GramaticalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GramaticalCategory
        fields = ('abbreviation', 'title')
