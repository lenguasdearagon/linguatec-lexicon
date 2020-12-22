from background_task import background

from .importers import import_data, import_variation, load_gramcats
from .exporters import write_to_csv_file_data, write_to_csv_file_variation

from .models import ImportLog


@background(schedule=0)
def import_data_words(xlsx_file, lexicon_id, imports_info_id, dry_run):
    if imports_info_id is not None:
        ii = ImportLog.objects.get(pk=imports_info_id)
        ii.status = ImportLog.RUNNING
        ii.save()
    return import_data(xlsx_file, lexicon_id, dry_run, False, imports_info_id)


@background(schedule=0)
def import_variation_entries(xlsx_file, lexicon_id, variation_name, imports_info_id, dry_run):
    if imports_info_id is not None:
        ii = ImportLog.objects.get(pk=imports_info_id)
        ii.status = ImportLog.RUNNING
        ii.save()
    return import_variation(xlsx_file, lexicon_id, variation_name, dry_run, imports_info_id)


@background(schedule=0)
def load_data_gramcats(csv_files, imports_info_id):
    ii = ImportLog.objects.get(pk=imports_info_id)
    ii.status = ImportLog.RUNNING
    ii.save()
    return load_gramcats(csv_files, imports_info_id)


@background(schedule=0)
def write_to_csv_file_export_data(lexicon, output_file):
    return write_to_csv_file_data(lexicon, output_file)


@background(schedule=0)
def write_to_csv_file_export_variation(lexicon_id, variation_id, output_file):
    return write_to_csv_file_variation(lexicon_id, variation_id, output_file)
