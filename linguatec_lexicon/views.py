from django.shortcuts import render
from rest_framework import viewsets

from .models import Word
from .serializers import WordSerializer


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows words to be viewed.
    """
    queryset = Word.objects.all().order_by('term')
    serializer_class = WordSerializer