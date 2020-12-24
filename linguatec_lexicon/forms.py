from django import forms
from django.core import validators


class ValidatorForm(forms.Form):
    input_file = forms.FileField(
        validators=[validators.FileExtensionValidator(allowed_extensions=["xlsx"])])


class CSVValidatorForm(forms.Form):
    input_file = forms.FileField(
        validators=[validators.FileExtensionValidator(allowed_extensions=["csv"])])
