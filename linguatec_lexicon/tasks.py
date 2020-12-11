from background_task import background

from .importers import import_variation, load_gramcats
from .exporters import write_to_csv_file_data, write_to_csv_file_variation


@background(schedule=30)
def import_variation_entries(csv_files, lexicon_id, variation_id):
    return import_variation(csv_files, lexicon_id, variation_id, False)


@background(schedule=30)
def load_data_gramcats(csv_files):
    return load_gramcats(csv_files)


@background(schedule=30)
def write_to_csv_file_export_data(lexicon, output_file):
    return write_to_csv_file_data(lexicon, output_file)


@background(schedule=30)
def write_to_csv_file_export_variation(lexicon_id, variation_id, output_file):
    return write_to_csv_file_variation(lexicon_id, variation_id, output_file)
