# LINGUATEC lexicon

An online bilingual dictionary developed inside the LINGUATEC project
with the purpose of host a Spanish to Aragonese dictionary.

## Development installation

Get the app code:
```bash
git clone git@gitlab.com:slamora/linguatec-lexicon.git
```

Create devel project site
```bash
apt-get install --no-install-recommends python3-pip
pip3 install virtualenv

# create virtualenv and install requirements (included Django)
virtualenv env
source env/bin/activate
pip3 install -r linguatec-lexicon/requirements.txt

# add app source code as python site-package
# checking that has been linked properly
pip3 install -e linguatec-lexicon/
python -c "import linguatec_lexicon; print(linguatec_lexicon.get_version())"

# create a project (name it as you want!)
django-admin startproject mysite --template=linguatec-lexicon/linguatec_lexicon/conf/project_template
```

Run migrations, start development server and go to http://127.0.0.1:8000/api/
```bash
cd mysite
python manage.py migrate
python manage.py runserver
```

You got it! Let's start creating magical code!

### (Optional) Load sample data
Download sample data file and load it:
```bash
cd mysite
wget https://gitlab.com/slamora/linguatec-lexicon/raw/3-data-import/linguatec_lexicon/fixtures/sample-output.json?inline=false -o sample-output.json
python manage.py loaddata sample-output.json
```
