# User guide

## Importing data of an XLSX file
This software provides a cli command to import data from a calc sheet document. There are some examples on [tests/fixtures/](tests/fixtures/) folder.

Before performing an import you should initialize the database with a list of accepted gramatical categories. You can do that using `importgramcat` utility.
```bash
python manage.py importgramcat path_to_gramcats.csv
```

Input data example:
```csv
"abbreviation","title"
"adj.","adjetive"
"n.","noun"
```

**NOTE:** [gramcat-es-ar.csv](linguatec_lexicon/fixtures/gramcat-es-ar.csv) is an example of CSV containing gramcats.


To run `importdata` utility go to the root of your project and execute:
```bash
python manage.py importdata path_to_datasheet.xlsx
```

Input data example:

| A | B | C | D (ignored column) | E (optional) | F (only for verbs) |
| ------ | ------ | ------ | ------ | ------ | ------ |
| first-word | first-gramcat | first-entry |  | first-example | first-verbal-conjugation |
| second-word | second-gramcat | second-entry |  | ... | ... |

**NOTE:** the data will be write to database only if there is no errors during the validation process.
