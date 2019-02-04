#!/bin/bash

ssbin='/path/to/sonar-scanner'
# note: point to the part of git repo that contains the django app to avoid
# errors outside the source code analysis
backpath='/path/to/linguatec-lexicon'
backauth='xxxxxxxxxxxxxxxXXxxxxXXxxXxxxxxxxxxxxxxx'
backkey='backendkey'
backcoveragepath='/path/to/mysite/coverage.xml'
backbanditpath='/path/to/bandit-report.json'
frontpath='/path/to/linguatec-lexicon-frontend'
frontauth='XxXxxxxxxXXxxXxxXXxxxXxxxXXxxXXxxxxxxxxx'
frontkey='frontendkey'
myurl='http://127.0.0.1:9000'

envpath='/path/to/env/bin/activate'
. "$envpath"

# go strictly to the python source code
cd "$backpath"/linguatec_lexicon
git pull
"$ssbin" \
  -Dsonar.projectKey="$backkey" \
  -Dsonar.sources=. \
  -Dsonar.host.url="$myurl" \
  -Dsonar.login="$backauth" \
  -Dsonar.python.coverage.reportPath="$backcoveragepath" \
  -Dsonar.python.bandit.reportPaths="$backbanditpath"

cd "$frontpath"
git pull
"$ssbin" \
  -Dsonar.projectKey="$frontkey" \
  -Dsonar.sources=. \
  -Dsonar.host.url="$myurl" \
  -Dsonar.login="$frontauth"
