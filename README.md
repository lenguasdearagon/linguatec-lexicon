# LINGUATEC lexicon

Diccionario online de aragonés dentro del proyecto LINGUATEC.

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
# this is temp, comming soon `pip install linguatec_lexicon` magic
#bug, in debian stable (and gitlab ci) it is python3.5
#echo `pwd`/linguatec-lexicon/ > env/lib/python3.6/site-packages/linguatec_lexicon.pth
#fix -> wildcar in redirection operator from bash src https://stackoverflow.com/questions/15315664/bash-redirection-with-wildcard
for mypath in env/lib/python*; do echo `pwd`/linguatec-lexicon/ > $mypath/site-packages/linguatec_lexicon.pth; done
python -c "import linguatec_lexicon"

# create a project (name it as you want!)
django-admin startproject mysite
```

Add `linguatec_lexicon` to `INSTALLED_APPS`
```python
# mysite/mysite/settings.py

INSTALLED_APPS = [
     ...
    'linguatec_lexicon',
]
```

TODO: include urls.py on mysite.url (when this file exists)

# Run migrations and start development server!
```bash
cd mysite
python manage.py migrate
python manage.py runserver
```

You got it! Let's start creating magical code!
