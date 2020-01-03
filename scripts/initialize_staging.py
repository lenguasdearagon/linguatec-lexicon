import getopt
import os
import sys

import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linguatec.settings')
try:
    django.setup()
except django.core.exceptions.ImproperlyConfigured:
    print("""
        You must define the environment variable DJANGO_SETTINGS_MODULE. Run:
            DJANGO_SETTINGS_MODULE="linguatec.settings"
            export DJANGO_SETTINGS_MODULE
    """)
    sys.exit(2)


from linguatec_lexicon.models import (DiatopicVariation, GramaticalCategory,
                                      Lexicon, Region)


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
    Ribagorza	    benasqués	            Benas.
    Ribagorza	    bajorribagorzano    	Ribag.
    Sobrarbe	    chistabín	            Chist.
    Sobrarbe	    belsetán	            Belset.
    Sobrarbe	    habla de Sobrepuerto	Sobrep.
    Alto Gállego	panticuto	            Pant.
    Alto Gállego	tensino                 Tens.
    Jacetania   	cheso	                Cheso
    Jacetania	    ansotano    	        Ansot.

    """

    # Create Regions
    ribagorza = Region.objects.create(name="Ribagorza")
    sobrarbe = Region.objects.create(name="Sobrarbe")
    # TODO complete creation of all regions

    # Create DiatopicVariation
    DiatopicVariation.objects.create(
        name="benasqués",
        abbreviation="Benas.",
        region=ribagorza,
    )

    DiatopicVariation.objects.create(
        name="bajorribagorzano",
        abbreviation="Ribag.",
        region=ribagorza,
    )

    DiatopicVariation.objects.create(
        name="chistabín",
        abbreviation="Chist.",
        region=sobrarbe,
    )
    # TODO complete with all diatopic variations


def main():
    print("""
        0. Run migrations
        ./manage.py migrate
    """)

    print("\t1. Creating Lexicon")
    # init_lexicon()

    print("\t2. Creating regions and diatopic variations")
    # init_diatopic_variations()

    print("""
        3. To import gramatical categories run:
            ./manage.py importgramcat --purge linguatec-lexicon/tests/fixtures/gramcat-es-ar.csv

        4. To import data (common aragonese) run:
            ./manage.py importdata vocabulario-castellano-aragones.xlsx

        5. To import diatopic variations data run:
            ./manage.py importvariation variation_file.xlsx --variation variation_name --verbosity 3 --dry-run
    """)


def drop_all():
    DiatopicVariation.objects.all().delete()
    Region.objects.all().delete()
    Lexicon.objects.all().delete()


if __name__ == '__main__':
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "h", ["help", "drop"])
    except getopt.GetoptError:
        print('{} [--drop]'.format(sys.argv[0]))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('{} [--drop]'.format(sys.argv[0]))
            sys.exit()
        elif opt == "--drop":
            drop_all()
            sys.exit()

    main()
