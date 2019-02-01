# Admin guide

## Initialize the dictionary content
After installing the app probably you will want to put some content on it.
This software provides two cli commands that will help you in this process: `importgramcat` and `importdata`

First of all you need to import the accepted gramatical categories for your dictionary.
1. Put the content in a CSV file following the same schema as the [gramcat sample](fixtures/gramcat-es-ar.csv).
2. Run the following command:
```bash
python manage.py importgramcat path_to_your_gramcat.csv
```

After that, only one step more is required to import the rest of the content. Just run:
```bash
python manage.py importdata path_to_your_content.xlsx
```
Yap! You have your content available!
