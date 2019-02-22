import json
import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .forms import ValidatorForm
from .models import GramaticalCategory, Word
from .serializers import GramaticalCategorySerializer, WordSerializer, WordNearSerializer


class DataValidatorView(TemplateView):
    template_name = "linguatec_lexicon/datavalidator.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = ValidatorForm(request.POST, request.FILES)

        if form.is_valid():
            xlsx_file = form.cleaned_data['input_file']

            # store uploaded file as a temporal file
            tmp_fd, tmp_file = tempfile.mkstemp()
            f = os.fdopen(tmp_fd, 'wb')  # open the tmp file for writing
            f.write(xlsx_file.read())  # write the tmp file
            f.close()

            # validate user file
            out = StringIO()
            call_command('importdata', tmp_file, dry_run=True, no_color=True, verbosity=3, stdout=out)

            context['input_file'] = form.cleaned_data['input_file']

            errors = []
            for line in out.getvalue().split('\n'):
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    continue
                errors.append(data)

            context['errors'] = errors
            return self.render_to_response(context)

        context['form'] = form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ValidatorForm()
        return context


class DefaultLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 30
    max_limit = 100


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows words to be viewed.
    """
    queryset = Word.objects.all().order_by('term')
    serializer_class = WordSerializer
    pagination_class = DefaultLimitOffsetPagination

    @action(detail=False)
    def near(self, request):
        self.serializer_class = WordNearSerializer
        query = self.request.query_params.get('q', None)
        queryset = Word.objects.search_near(query)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def search(self, request):
        query = self.request.query_params.get('q', None)
        if query is not None:
            query = query.strip()

        queryset = Word.objects.search(query)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GramaticalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows words to be retrieved.
    """
    queryset = GramaticalCategory.objects.all().order_by('abbreviation')
    serializer_class = GramaticalCategorySerializer
    pagination_class = DefaultLimitOffsetPagination

    @action(detail=False, )
    def show(self, request):
        abbr = self.request.query_params.get('abbr', None)

        gramcat = get_object_or_404(self.queryset, abbreviation=abbr)

        serializer = self.get_serializer(gramcat)
        return Response(serializer.data)
