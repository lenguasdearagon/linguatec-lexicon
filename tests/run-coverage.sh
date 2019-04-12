#!/bin/bash
envpath='/root/linguatec-sonarqube/projects/env/bin/activate'
. "$envpath"
sourcepath='/path/to/linguatec-lexicon/linguatec_lexicon'

cd "$sourcepath"
coverage erase
coverage run --source "$sourcepath" runtests.py --parallel 1
# debug
# coverage report
coverage xml -i
