#!/bin/bash
# You could use a custom path setting $LEX_PATH as environment variable

# exit when any command fails
set -e

. env/bin/activate

export DJANGO_COLORS="notice=yellow"

./manage.py initialize_staging --drop
./manage.py initialize_staging

LEX_PATH=${LEX_PATH:-/home/santiago/trabajo/dgpl/linguatec-v6-vocabularios-temáticos/contenido}

time ./manage.py importdata -v3 es-ar $LEX_PATH/vocabulario-castellano-aragones-2022-12-26.xlsx
# Imported: 26332 words, 29948 entries, 337 examples

time ./manage.py importdata -v3 es-ar@law $LEX_PATH/vocabulario-jurídico-Aragonario-2022-11-17bis.xlsx
# Imported: 4415 words, 4422 entries, 0 examples

time ./manage.py importdata -v3 es-ar@flora $LEX_PATH/vocabulario-VECHETALS-2022-12-21.xlsx
# Imported: 1473 words, 1564 entries, 1562 examples

time ./manage.py importdata -v3 es-ar@fauna $LEX_PATH/vocabulario-FAUNA-2022-12-22.xlsx
# Imported: 1620 words, 1626 entries, 1626 examples


# -- COPY OF initialize_staging QUICKSTART
export LINGUATEC_AR_ES_PATH="$LEX_PATH/ar-es/"
export LINGUATEC_VARIANTS_PATH="$LEX_PATH/variedades/"

time ./manage.py initialize_staging --import-aragonese
time ./manage.py initialize_staging --import-variations
time python manage.py marktranslations

echo "END OF SCRIPT!"
