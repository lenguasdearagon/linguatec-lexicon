# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## master
- [fixed] `importvariation` handle properly variation param on dry-run.
- [fixed] Issue #83 searchs that starts with signs of punctuation.

## [0.3.1] - 2020-01-16
- [changed] `importvariation` supports XLSX with multiple sheets.
- [changed] `importvariation` provide default gramcat when column B is missing (or
    error if getting default fails).
- [fixed] `importvariation` error when translation (column C) is missing.

## [0.3] - 2020-01-03
- [added] Diatopic variation validator view.
- [changed] `--variation` is optional on `importvariation` management command.
- [fixed]: `importvariation` ignore extra columns on XLSX file.

## [0.2] - 2019-07-29
- [added] Add support to diatopic variations
- [fixed] duplicated word gramcats

## [0.1] - 2019-04-12
- [added] API: retrieve and search words by term.
- [added] API: retrieve gramatical categories.
- [added] Add view to validate XLSX data.
