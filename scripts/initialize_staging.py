#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import os
import sys

import django
from django.core import management
from django.utils import timezone

try:
    django.setup()
except django.core.exceptions.ImproperlyConfigured:
    print("""
        You must define the environment variable DJANGO_SETTINGS_MODULE. Run:
            export DJANGO_SETTINGS_MODULE=aragonario.settings
    """)
    sys.exit(2)


from linguatec_lexicon.models import (DiatopicVariation, Lexicon, Region)


AR_ES_PATH = os.getenv('LINGUATEC_AR_ES_PATH', '~/data/ar-es/')
VARIANTS_PATH = os.getenv('LINGUATEC_VARIANTS_PATH', '~/data/variedades')


def init_lexicon():
    Lexicon.objects.create(
        name="castellano-aragonés",
        description="",
        src_language="es",
        dst_language="ar"
    )
    Lexicon.objects.create(
        name="aragonés-castellano",
        description="",
        src_language="ar",
        dst_language="es"
    )


def init_diatopic_variations():
    """
    COMARCA         VARIEDAD	            ABREVIATURA
    ----------------------------------------------------
    Alto Gállego	tensino                 Tens.
    Alto Gállego	tensino panticuto       Pant.
    Jacetania   	cheso	                Cheso
    Jacetania	    ansotano    	        Ansot.
    Ribagorza	    benasqués	            Benas.
    Ribagorza	    bajorribagorzano    	Ribag.
    Sobrarbe	    chistabín	            Chist.
    Sobrarbe	    belsetán	            Belset.
    Sobrarbe	    habla de Sobrepuerto	Sobrep.
    Somontano       Somontanos              Somon.
    """

    # Create Regions
    def create_region(name):
        return Region.objects.create(name=name)

    alto_gallego = create_region("Alto Gállego")
    jacetania = create_region("Jacetania")
    ribagorza = create_region("Ribagorza")
    sobrarbe = create_region("Sobrarbe")
    somontano = create_region("Somontanos")

    def create_variation(region, name, abbr):
        return DiatopicVariation.objects.create(
            name=name,
            abbreviation=abbr,
            region=region,
        )

    # Create DiatopicVariations
    create_variation(alto_gallego, "Tensino", "Tens.")
    create_variation(alto_gallego, "Tensino Panticuto", "Pant.")
    create_variation(jacetania, "Ansotano", "Ansot.")
    create_variation(jacetania, "Cheso", "Cheso")
    create_variation(ribagorza, "Bajorribagorzano", "Ribag.")
    create_variation(ribagorza, "Benasqués", "Benas.")
    create_variation(sobrarbe, "Belsetán", "Belset.")
    create_variation(sobrarbe, "Chistabín", "Chist.")
    create_variation(sobrarbe, "Habla de Sobrepuerto", "Sobrep.")
    create_variation(somontano, "Somontanos", "Somon.")


VARIANTS_MAPPING = {
    "Tensino": "ALTO GÁLLEGO-tensino-2021-07-15.xlsx",
    "Tensino Panticuto": "ALTO GÁLLEGO-tensino-panticuto-2021-06-08.xlsx",
    "Ansotano": "JACETANIA-ansotano-2021-08-20.xlsx",
    "Cheso": "JACETANIA-cheso-2021-06-08.xlsx",
    "Bajorribagorzano": "RIBAGORZA-baixoribagorzano-2021-06-08.xlsx",
    "Benasqués": "RIBAGORZA-benasques-2021-06-08.xlsx",
    "Belsetán": "SOBRARBE-belsetán-2021-06-08.xlsx",
    "Chistabín": "SOBRARBE-chistabín-2021-06-22.xlsx",
    "Habla de Sobrepuerto": "SOBRARBE-sobrepuerto-2021-08-20.xlsx",
    "Somontanos": "SOMONTANO-2021-08-12.xlsx",
}


def validate_variations():
    for _, xlsx in VARIANTS_MAPPING.items():
        xlsx_fullpath = os.path.join(VARIANTS_PATH, xlsx)
        print("-" * 80)
        print(xlsx_fullpath)
        management.call_command('importvariation', 'es-ar', xlsx_fullpath, verbosity=3, dry_run=True)


def import_variations():
    for variation, xlsx in VARIANTS_MAPPING.items():
        print("-" * 80)
        print(variation, xlsx)
        xlsx_fullpath = os.path.join(VARIANTS_PATH, xlsx)
        management.call_command('importvariation', 'es-ar', xlsx_fullpath, verbosity=3, variation=variation)


def main():
    print("""
        0. Run migrations
        ./manage.py migrate
    """)

    print("\t1. Creating Lexicon")
    init_lexicon()

    print("\t2. Creating regions and diatopic variations")
    init_diatopic_variations()

    print("""
        3. To import gramatical categories run:
            ./manage.py importgramcat --purge linguatec-lexicon/tests/fixtures/gramcat-es-ar.csv

        4. To import data (common aragonese) run:
            ./manage.py importdata vocabulario-castellano-aragones.xlsx

        5. To import diatopic variations data run:
            ./manage.py importvariation lex_code variation_file.xlsx --variation variation_name --verbosity 3 --dry-run
    """)


def help():
    USAGE = ("""
             USAGE
             ---------------
             {} [--drop]
             """
             )
    print(USAGE.format(sys.argv[0]))

    print("""
QUICK START
-------------------
date
export DJANGO_SETTINGS_MODULE="lenguasaragon.settings_postgres"
export LINGUATEC_AR_ES_PATH="/home/santiago/trabajo/dgpl/linguatec-v5/ar-es/"
export LINGUATEC_VARIANTS_PATH="/home/santiago/trabajo/dgpl/linguatec-v5/variedades/"

python initialize_staging.py --drop
python initialize_staging.py
time ./manage.py importdata -v3 es-ar ~/trabajo/dgpl/linguatec-v5/vocabulario-castellano-aragones-2021-08-12.xlsx
time python initialize_staging.py --import-aragonese

#python initialize_staging.py --validate-variations

time python initialize_staging.py --import-variations
time python manage.py marktranslations

date
echo "FIN"
# to validate a single variation
./manage.py importvariation -v3 --dry-run es-ar ~/trabajo/dgpl/linguatec-v4/variedades/SOMONTANO-2021-06-22.xlsx

# to import a single variation file
# ./manage.py importvariation -v3 --variation "Ansotano" es-ar ~/trabajo/dgpl/linguatec-v4/variedades/JACETANIA-ansotano-2021-06-08.xlsx
    """)


def import_aragonese_spanish_data():
    ls_files = sorted(os.listdir(AR_ES_PATH))

    for filename in ls_files:
        filepath = os.path.join(AR_ES_PATH, filename)
        start = timezone.now()
        management.call_command('importdata', 'ar-es', filepath, verbosity=3)  # , dry_run=True)
        end = timezone.now()
        print(end - start)


def drop_all():
    DiatopicVariation.objects.all().delete()
    Region.objects.all().delete()
    Lexicon.objects.all().delete()


if __name__ == '__main__':
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "h", ["help", "drop", "validate-variations", "import-variations", "import-aragonese"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help()
            sys.exit()
        elif opt == "--drop":
            drop_all()
            sys.exit()
        elif opt == "--validate-variations":
            validate_variations()
            sys.exit()
        elif opt == "--import-variations":
            import_variations()
            sys.exit()
        elif opt == "--import-aragonese":
            import_aragonese_spanish_data()
            sys.exit()

    main()
