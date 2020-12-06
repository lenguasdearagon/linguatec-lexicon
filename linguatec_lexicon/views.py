import json
import os
import tempfile
from io import StringIO

from .tasks import write_to_csv_file_export_data, write_to_csv_file_export_variation

from django.core.management import call_command
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .forms import ValidatorForm
from .models import GramaticalCategory, Word, Lexicon
from .serializers import GramaticalCategorySerializer, WordSerializer, WordNearSerializer, LexiconSerializer


class DataValidatorView(TemplateView):
    template_name = "linguatec_lexicon/datavalidator.html"
    title = "Data validator"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = ValidatorForm(request.POST, request.FILES)

        if form.is_valid():
            xlsx_file = form.cleaned_data['input_file']

            # store uploaded file as a temporal file
            tmp_fd, tmp_file = tempfile.mkstemp(suffix='.xlsx')
            f = os.fdopen(tmp_fd, 'wb')  # open the tmp file for writing
            f.write(xlsx_file.read())  # write the tmp file
            f.close()

            # validate uploaded file and handle errors (if any)
            out = self.validate(tmp_file)
            errors = []
            for line in out.getvalue().split('\n'):
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                errors.append(data)

            context.update({
                'errors': errors,
                'input_file': xlsx_file,
            })
            return self.render_to_response(context)

        context['form'] = form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form':  ValidatorForm(),
            'title': self.title,
        })
        return context

    def validate(self, xlsx_file):
        out = StringIO()
        call_command('importdata', xlsx_file, dry_run=True, no_color=True, verbosity=3, stdout=out)
        return out


class DiatopicVariationValidatorView(DataValidatorView):
    title = "Diatopic variation validator"

    def validate(self, xlsx_file):
        out = StringIO()
        call_command('importvariation', xlsx_file, dry_run=True, no_color=True, verbosity=3, stdout=out)
        return out


class ExportData(TemplateView):
    template_name = "linguatec_lexicon/exportdata.html"
    title = "Export Data"
    title2 = "Export Variation"

    def post(self, request, *args, **kwargs):
        type_export = str(request.POST.get('type_export'))

        if type_export == 'lexicon':
            lexicon_code = str(request.POST.get('lexicon'))
            lexicon_id = Lexicon.objects.get(src_language=lexicon_code[:2], dst_language=lexicon_code[3:]).pk

            return write_to_csv_file_export_data.now(lexicon_id, None)

        elif type_export == 'variation':
            lexicon_code = str(request.POST.get('lexicon'))
            lexicon_id = Lexicon.objects.get(src_language=lexicon_code[:2], dst_language=lexicon_code[3:]).pk

            variation = str(request.POST.get('variation'))

            return write_to_csv_file_export_variation.now(variation, None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'title2': self.title2,
        })
        return context

    def validate(self, xlsx_file):
        out = StringIO()
        call_command('importdata', xlsx_file, dry_run=True, no_color=True, verbosity=3, stdout=out)
        return out


class DefaultLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 30
    max_limit = 100


class LexiconViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows lexicons to be viewed.
    """
    queryset = Lexicon.objects.all().order_by('src_language', 'dst_language')
    serializer_class = LexiconSerializer
    pagination_class = DefaultLimitOffsetPagination


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
        lex = self.request.query_params.get('l', '')
        lex = lex.strip()
        queryset = Word.objects.search_near(query, lex)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def search(self, request):
        query = self.request.query_params.get('q', None)
        lex = self.request.query_params.get('l', '')
        if query is not None:
            query = query.strip()
        lex = lex.strip()
        queryset = Word.objects.search(query, lex)
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
