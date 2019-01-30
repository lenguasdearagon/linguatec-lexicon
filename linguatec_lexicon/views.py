import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.shortcuts import render
from django.views.generic.base import TemplateView
from rest_framework import filters, viewsets

from .forms import ValidatorForm
from .models import Word
from .serializers import WordSerializer


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
            call_command('data-import', tmp_file, dry_run=True, no_color=True, verbosity=3, stdout=out)

            context['input_file'] = form.cleaned_data['input_file']

            context['errors'] = out.getvalue().split('\n')
            return self.render_to_response(context)

        context['form'] = form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ValidatorForm()
        return context


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows words to be viewed.
    """
    queryset = Word.objects.all().order_by('term')
    serializer_class = WordSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('term',)
