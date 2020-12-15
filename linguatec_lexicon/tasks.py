from background_task import background

from .importers import import_data, import_variation, load_gramcats
from .exporters import write_to_csv_file_data, write_to_csv_file_variation

from .models import ImportsInfo


@background(schedule=30)
def import_data_words(csv_files, lexicon_id, imports_info_id):
    ii = ImportsInfo.objects.get(pk=imports_info_id)
    ii.status = ImportsInfo.RUNNING
    ii.save()
    return import_data(csv_files, lexicon_id, False, False, imports_info_id)


@background(schedule=30)
def import_variation_entries(csv_files, lexicon_id, variation_name, imports_info_id):
    ii = ImportsInfo.objects.get(pk=imports_info_id)
    ii.status = ImportsInfo.RUNNING
    ii.save()
    return import_variation(csv_files, lexicon_id, variation_name, False, imports_info_id)


@background(schedule=30)
def load_data_gramcats(csv_files, imports_info_id):
    ii = ImportsInfo.objects.get(pk=imports_info_id)
    ii.status = ImportsInfo.RUNNING
    ii.save()
    return load_gramcats(csv_files, imports_info_id)


@background(schedule=30)
def write_to_csv_file_export_data(lexicon, output_file):
    return write_to_csv_file_data(lexicon, output_file)


@background(schedule=30)
def write_to_csv_file_export_variation(lexicon_id, variation_id, output_file):
    return write_to_csv_file_variation(lexicon_id, variation_id, output_file)
