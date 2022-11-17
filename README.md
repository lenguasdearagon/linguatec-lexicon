# LINGUATEC lexicon

An online bilingual dictionary developed inside the LINGUATEC project
with the purpose of host a Spanish to Aragonese dictionary.

## API REST reference
You can check the linguatec-lexicon API reference on [Swagger Hub](https://app.swaggerhub.com/apis-docs/ribaguifi/linguatec-lexicon). If you find any issue or you want to use another service to see the schema, you can find a local copy on [docs/api-schema.yml](docs/api-schema.yml)

## Development installation

Get the app code:
```bash
git clone https://github.com/lenguasdearagon/aragonario.git
```

Create devel project site
```bash
apt-get install --no-install-recommends python3-pip

# create virtualenv and install requirements (included Django)
python3 -m venv env
. env/bin/activate
pip install -r aragonario/requirements.txt

# add app source code as python site-package
# checking that has been linked properly
pip install -e aragonario/
python -c "import linguatec_lexicon; print(linguatec_lexicon.get_version())"

# create a project (name it as you want!)
django-admin startproject mysite --template=aragonario/linguatec_lexicon/conf/project_template
```

Run migrations, start development server and go to http://127.0.0.1:8000/api/
```bash
cd mysite
python manage.py migrate
python manage.py runserver
```

You got it! Let's start creating magical code!

### (Optional) Load sample data
Download [sample data](linguatec_lexicon/fixtures/lexicon-sample.json) file and load it:
```bash
cd mysite
python manage.py loaddata lexicon-sample.json
```

### Running tests
To run the tests, clone the repository, and then:

```bash
# Setup the virtual environment
virtualenv env
source env/bin/activate
git clone https://github.com/lenguasdearagon/aragonario.git
cd aragonario/
pip install -r requirements.txt
pip install .

# Run the tests
./runtests.py
```

#### tests coverage
To run tests coverage:
1. Install coverage package:
    pip install coverage

2. Run coverage command. **IMPORTANT** tests should be run by a only process, check [coverage docs](https://coverage.readthedocs.io/en/latest/subprocess.html) for more details.
    coverage run --source linguatec_lexicon runtests.py --settings tests.settings_postgres --parallel 1
    coverage html

3. Visit linguatec-lexicon/htmlcov/index.html with your favourite browser.
