#!/bin/bash

srcpath='/path/to/linguatec-lexicon/linguatec_lexicon'
outpath='/path/to/bandit-report.json'

envpath='/path/to/env/bin/activate'
. "$envpath"

bandit --format json --output "$outpath" --recursive "$srcpath"
