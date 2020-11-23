import json
import pandas as pd

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from linguatec_lexicon.models import (
    Entry, Lexicon, GramaticalCategory, DiatopicVariation, Word)

import csv
import argparse
import os.path

def get_src_language_from_lexicon_code(lex_code):
    return lex_code[:2]

def get_dst_language_from_lexicon_code(lex_code):
    return lex_code[3:]



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'lexicon_code', type=str,
            help="Select the lexicon code where data will be exported from",
        )

        parser.add_argument(
            'variation_name', type=str,
            help="The variation name of the variation chosen to export the data",
        )

        parser.add_argument(
            'output_file', type=str,
            help='Name of file where data will be written to. (must be a csv file)'
        )


    def handle(self, *args, **options):
        self.lexicon_code = options['lexicon_code']
        self.variation_name = options['variation_name']
        self.output_file = options['output_file']
        # check that a lexicon with that code exist
        try:
            src = get_src_language_from_lexicon_code(self.lexicon_code)
            dst = get_dst_language_from_lexicon_code(self.lexicon_code)

            self.lexicon = Lexicon.objects.get(src_language = src, dst_language = dst)
        except Lexicon.DoesNotExist:
            raise CommandError('Error: There is not a lexicon with that code: ' + self.lexicon_code)
        

        try:
            self.variation = DiatopicVariation.objects.get(name=self.variation_name)
        except DiatopicVariation.DoesNotExist:
            raise CommandError('Error: There is not a diatopic variation with that name: ' + self.variation_name)

        #check if csv file already exists
        if os.path.isfile(self.output_file):
            raise CommandError('Error: A csv with that name already exists: ' + self.output_file)
        
        self.write_to_csv_file()



    def write_to_csv_file(self):

        entry_list = list(Entry.objects.filter(variation=self.variation))
        
        word_list = []
        for entry in entry_list:
            word_list.append(entry.word)
        word_list = list(set(word_list))

        word_ordered_list = []
        for word in Word.objects.filter(lexicon=self.lexicon).order_by('term'):
            if word in word_list:
                word_ordered_list.append(word)

        with open(self.output_file, 'w') as outfile:
            writer = csv.writer(outfile, delimiter=';')
            for word in word_ordered_list:

                write_list = [
                    '', #word
                    [], #gramcats
                    [], #translation
                ]

                write_list[0] = word.term

                sub_entry_list = Entry.objects.filter(word=word, variation=self.variation)
                for entry in sub_entry_list:
                
                    gramcat_list = list(entry.gramcats.all())
                    for gram in gramcat_list:
                        write_list[1].append(gram.abbreviation)
                    
                    write_list[2].append(entry.translation)

                write_list[1] = list(set(write_list[1]))
                write_list[1].sort()
                write_list[1] = ' // '.join(write_list[1])
                write_list[2] = ' // '.join(write_list[2])
                writer.writerow(write_list)
                    
                    

        


                
