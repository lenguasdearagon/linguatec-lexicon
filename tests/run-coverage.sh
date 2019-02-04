#!/bin/bash

sitepath='/path/to/mysite/'

envpath='/path/to/env/bin/activate'
. "$envpath"

cd "$sitepath"
coverage erase
coverage run --source '.,/path/to/linguatec-lexicon/linguatec_lexicon' manage.py test linguatec_lexicon
# debug
# coverage report
coverage xml -i
