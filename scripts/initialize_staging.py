#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import os
import sys

import django
from django.core import management

try:
    django.setup()
except django.core.exceptions.ImproperlyConfigured:
    print("""
        You must define the environment variable DJANGO_SETTINGS_MODULE. Run:
            DJANGO_SETTINGS_MODULE="linguatec.settings"
            export DJANGO_SETTINGS_MODULE
    """)
    sys.exit(2)


from linguatec_lexicon.models import (DiatopicVariation, Lexicon, Region)


def init_lexicon():
    Lexicon.objects.create(
        name="diccionario linguatec",
        description="",
        src_language="es",
        dst_language="ar"
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
    "Tensino": "ALTO GÁLLEGO-tensino-2020-01-20.xlsx",
    "Tensino Panticuto": "ALTO GÁLLEGO-tensino-panticuto-2020-01-20.xlsx",
    "Ansotano": "JACETANIA-ansotano-2020-01-20.xlsx",
    "Cheso": "JACETANIA-cheso-2020-01-20.xlsx",
    "Bajorribagorzano": "RIBAGORZA-baixoribagorzano-2020-01-20.xlsx",
    "Benasqués": "RIBAGORZA-benasques-2020-01-20.xlsx",
    "Belsetán": "SOBRARBE-belsetán-2020-01-20.xlsx",
    "Chistabín": "SOBRARBE-chistabín-2020-01-20.xlsx",
    "Habla de Sobrepuerto": "SOBRARBE-sobrepuerto-2020-01-20.xlsx",
    "Somontanos": "SOMONTANOS-2020-01-20.xlsx",
}

VARIANTS_PATH = '/home/santiago/trabajo/linguatec-v3/variedades'


def validate_variations():
    # for xlsx in os.listdir(VARIANTS_PATH):
    #     if not xlsx.endswith('xlsx'):
    #         continue
    for _, xlsx in VARIANTS_MAPPING.items():
        xlsx_fullpath = os.path.join(VARIANTS_PATH, xlsx)
        print("-" * 80)
        print(xlsx_fullpath)
        management.call_command('importvariation', xlsx_fullpath, 'es-ar', verbosity=3, dry_run=True)


def import_variations():
    for variation, xlsx in VARIANTS_MAPPING.items():
        print("-" * 80)
        print(variation, xlsx)
        xlsx_fullpath = os.path.join(VARIANTS_PATH, xlsx)
        management.call_command('importvariation', xlsx_fullpath, 'es-ar', verbosity=3, variation=variation)


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
            ./manage.py importvariation variation_file.xlsx lex_code --variation variation_name --verbosity 3 --dry-run
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
DJANGO_SETTINGS_MODULE="lenguasaragon.settings_postgres"
export DJANGO_SETTINGS_MODULE
python initialize_staging.py --drop
python initialize_staging.py
time ./manage.py importdata -v3 ~/trabajo/linguatec-v3/vocabulario-castellano-aragones-2020-01-27-az.xlsx

python initialize_staging.py --validate-variations
python initialize_staging.py --import-variations

# to import only a specific file
# ./manage.py importvariation -v3 --variation "Tensino" "ALTO GÁLLEGO-tensino-2020-01-20.xlsx es-ar"
    """)


def drop_all():
    DiatopicVariation.objects.all().delete()
    Region.objects.all().delete()
    Lexicon.objects.all().delete()


if __name__ == '__main__':
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "h", ["help", "drop", "validate-variations", "import-variations"])
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

    main()
