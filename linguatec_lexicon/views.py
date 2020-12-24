import json
import os
import tempfile
from io import StringIO

from .tasks import (write_to_csv_file_export_data, write_to_csv_file_export_variation,
                    load_data_gramcats, import_variation_entries, import_data_words)

from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .forms import ValidatorForm, CSVValidatorForm
from .models import GramaticalCategory, DiatopicVariation, Word, Lexicon, ImportLog
from .serializers import (GramaticalCategorySerializer, WordSerializer, WordNearSerializer,
                          LexiconSerializer, ImportLogSerializer)


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
            out = self.validate(tmp_file, request)
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
            'lexicon_list': Lexicon.objects.all(),
            'src_languages': Lexicon.objects.all().values('src_language').distinct(),
            'variation_list': None,
        })
        return context

    def validate(self, xlsx_file, request):
        lexicon_code = str(request.POST.get('lexicon_code'))
        out = StringIO()
        call_command('importdata', xlsx_file, lexicon_code, dry_run=True, no_color=True, verbosity=3, stdout=out)
        return out


class DiatopicVariationValidatorView(DataValidatorView):
    title = "Diatopic variation validator"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form':  ValidatorForm(),
            'title': self.title,
            'lexicon_list': Lexicon.objects.all(),
            'src_languages': Lexicon.objects.all().values('src_language').distinct(),
            'variation_list': DiatopicVariation.objects.all(),
        })
        return context

    def validate(self, xlsx_file, request):
        lexicon_code = str(request.POST.get('lexicon_code'))
        variation_name = str(request.POST.get('variation_name'))
        out = StringIO()
        call_command('importvariation', xlsx_file, lexicon_code, variation=variation_name,
                     dry_run=True, no_color=True, verbosity=3, stdout=out)
        return out


class ImportDataView(TemplateView):
    template_name = "linguatec_lexicon/importdata.html"

    def create_imports_info(self, input_file, type):
        ii = ImportLog.objects.create(status=ImportLog.CREATED, input_file=input_file, type=type)
        return ii.pk

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        type_import = str(request.POST.get('type_import'))

        if type_import == ImportLog.DATA or type_import == ImportLog.VARIATION:
            form = ValidatorForm(request.POST, request.FILES)
        if type_import == ImportLog.GRAMCATS:
            form = CSVValidatorForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['input_file']
            imports_info_id = self.create_imports_info(file, type_import)

            # store uploaded file as a temporal file
            if type_import == ImportLog.DATA or type_import == ImportLog.VARIATION:
                tmp_fd, tmp_file = tempfile.mkstemp(suffix='.xlsx')
            if type_import == ImportLog.GRAMCATS:
                tmp_fd, tmp_file = tempfile.mkstemp(suffix='.csv')
            f = os.fdopen(tmp_fd, 'wb')  # open the tmp file for writing
            f.write(file.read())  # write the tmp file
            f.close()

            if type_import == ImportLog.DATA:
                lexicon_code = str(request.POST.get('lexicon_code'))
                lexicon_id = Lexicon.objects.get_by_code(lexicon_code).pk
                import_data_words(tmp_file, lexicon_id, imports_info_id, False)

            if type_import == ImportLog.VARIATION:
                lexicon_code = str(request.POST.get('lexicon_code'))
                lexicon_id = Lexicon.objects.get_by_code(lexicon_code).pk
                variation_name = str(request.POST.get('variation_name'))
                import_variation_entries(tmp_file, lexicon_id, variation_name, imports_info_id, False)

            if type_import == ImportLog.GRAMCATS:
                load_data_gramcats([tmp_file], imports_info_id)

            context.update({
                'input_file': file,
                'is_finished': 'Importación realizada',
            })
            return self.render_to_response(context)

        context['form'] = form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form':  ValidatorForm(),
            'title_data': "Import Lexicon data",
            'title_variation': "Import Diatopic Variations",
            'title_gramcats': "Import Gramatical categories",
            'lexicon_list': Lexicon.objects.all(),
            'variation_list': DiatopicVariation.objects.all(),
        })
        return context


class ImportationsView(TemplateView):
    template_name = "linguatec_lexicon/importations.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        ii = ImportLog.objects.all()

        context.update({
                'importations': ii,
            })

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ImportationErrorsView(TemplateView):
    template_name = "linguatec_lexicon/importationerrors.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        ImportLog_id = int(request.GET.get('importation_id', None))
        ii = ImportLog.objects.get(pk=ImportLog_id)

        error_list = ii.list_errors()

        context.update({
                'status': ii.status,
                'type': ii.type,
                'created_at': ii.created_at,
                'num_rows': ii.num_rows,
                'input_file': ii.input_file,
                'errors': error_list,
            })

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ExportDataView(TemplateView):
    template_name = "linguatec_lexicon/exportdata.html"
    title = "Export Data"
    title2 = "Export Variation"

    def post(self, request, *args, **kwargs):
        TYPE_LEXICON = 'lexicon'
        TYPE_VARIATION = 'variation'

        type_export = str(request.POST.get('type_export'))

        if type_export == TYPE_LEXICON:
            lexicon_code = str(request.POST.get('lexicon_code'))
            lexicon_id = Lexicon.objects.get_by_code(lexicon_code).pk

            return write_to_csv_file_export_data.now(lexicon_id, None)

        elif type_export == TYPE_VARIATION:
            lexicon_code = str(request.POST.get('lexicon_code'))
            lexicon_id = Lexicon.objects.get_by_code(lexicon_code).pk

            variation_name = str(request.POST.get('variation_name'))
            variation_id = DiatopicVariation.objects.get(name=variation_name).pk

            return write_to_csv_file_export_variation.now(lexicon_id, variation_id, None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'title2': self.title2,
            'lexicon_list': Lexicon.objects.all(),
            'variation_list': DiatopicVariation.objects.all(),
        })
        return context


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
