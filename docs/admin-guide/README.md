# Admin guide

This is the guide to help on the installation and maintenance of this django app. It is intended to read from begin to end or to read just a particular section.

Note: the names suggested by the files and this guide are generic (frontend-site, backend-site, ...). Consider changing them for your particular deploy.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Admin guide](#admin-guide)
  - [Installation and deploy](#installation-and-deploy)
    - [Requirements](#requirements)
    - [General nginx config](#general-nginx-config)
    - [Backend](#backend)
      - [Database](#database)
      - [Web server](#web-server)
      - [WSGI](#wsgi)
    - [Frontend](#frontend)
      - [Web server](#web-server-1)
      - [WGSI](#wgsi)
  - [Maintenance](#maintenance)
    - [Frontend](#frontend-1)
    - [Backend](#backend-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installation and deploy

Take in account that [Requirements](#requirements) refer to general requirements and [General nginx config](#general-nginx-config) the configuration recommended both for frontend and backend.

### Requirements

It is recommended to use debian 9 stretch (the latest stable in this moment) or equivalent. Most of the dependencies from the debian package manager are used:

```
# install first dialog programs
apt update

apt=(
    git                            # to clone source repositories
    postgresql postgresql-contrib postgresql-client  # database
    nginx                          # webserver
    python3-pip                    # python repos
    python3-setuptools             # support tool python repos
    #temp disabled
    #memcached                      # cache system
    #python3-pylibmc                # python client for memcached

    # required for uwsgi build:
    build-essential
    python3-dev
    #libpcre3 libpcre3-dev          # perl regex url style? src https://stackoverflow.com/questions/21669354/rebuild-uwsgi-with-pcre-support

    vim                            # extra tool (temp?)
)

apt-get install --no-install-recommends -y ${apt[@]}
```

Except a few (virtualenv, wheel, uwsgi) that are obtained from pip:

```
# install wheel first, required for uwsgi build
pip3 install wheel

# these package requires to be installed through pip
pip=(
    https://projects.unbit.it/downloads/uwsgi-lts.tar.gz # LTS uwsgi -> git https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/uwsgi/
)

pip3 install ${pip[@]}
```

### General nginx config

General nginx configurations that apply both to frontend and backend.

Generate this key required for good security (it takes several minutes. Hint: use [tmux](https://en.wikipedia.org/wiki/Tmux), [screen](https://en.wikipedia.org/wiki/GNU_Screen) or another ssh session to continue with the configuration while this is being processed):

    openssl dhparam -out /etc/nginx/dhparam.pem 4096

Disable the default site provided by nginx:

    rm /etc/nginx/sites-enabled/default

Backup original configuration:

    mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.orig

And use this configuration [nginx.conf](nginx.conf) in `/etc/nginx/nginx.conf`.

To prevent undesirable random requests use [default-site.conf](nginx_default-site.conf) in /etc/nginx/sites-available/default-site.conf

Then enable default site:

    ln -s /etc/nginx/sites-available/default-site.conf /etc/nginx/sites-enabled/default-site.conf

### Backend

The backend is the part of the software that manages and processes the data in the appropriate way to its functioning.

Setup virtual environment setup for backend:

    python3 -m venv /srv/backend_proj_env
    source /srv/backend_proj_env/bin/activate

Get the source and install its particular dependencies:

    git clone https://github.com/lenguasdearagon/aragonario.git /srv/backend_git
    pip3 install -r /srv/backend_git/requirements.txt
    pip3 install -e /srv/backend_git/

Create, initialize the project and prepare static files for web server:

    cd /srv
    django-admin startproject backend_proj --template=/srv/backend_git/linguatec_lexicon/conf/project_template_backend
    cd /srv/backend_proj
    python3 manage.py collectstatic
    chown www-data: /srv/backend_proj

#### Database

The database stores the objects of the django application backend

Create the user for postgresql database:

    su - postgres -s /bin/bash -c "psql --command \"CREATE USER lexicon WITH SUPERUSER PASSWORD 'lexicon';\""

Create the database to operate the backend and sets the owner to the previous created user:

    su - postgres -s /bin/bash -c 'createdb -O lexicon lexicon'

The django backend models can be populated to the database:

    source /srv/backend_proj_env/bin/activate
    cd /srv/backend_proj
    python3 manage.py migrate

Final note: It is safe to use simple complexity in passwords if server is setup exclusively for this service (taking care who has access to it)

#### Web server

The web server component of the frontend is responsible of showing api.example.com

Save [uwsgi_params](nginx_uwsgi_params) in `/srv/backend_proj/uwsgi_params` and [backend-site.conf](nginx_backend-site.conf) in `/etc/nginx/sites-available/backend-site.conf`. After that, enable backend site:

    ln -s /etc/nginx/sites-available/backend-site.conf /etc/nginx/sites-enabled/backend-site.conf

And reload nginx:

    service nginx reload

#### WSGI

The wsgi component of the backend is responsible of making a bridge between the python code and the web server.

Create the directory if it does not exist:

    mkdir -p /etc/uwsgi

Save [backend-site.ini](uwsgi_backend-site.ini) in `/etc/uwsgi/backend-site.ini`

Configure `uwsgi-backend.service` for systemd saving [systemd_uwsgi_backend-site.service](systemd_uwsgi_backend-site.service) in `/etc/systemd/system/uwsgi-backend.service`

Enable service on boot:

    systemctl enable uwsgi-backend.service

Start it now:

    systemctl start uwsgi-backend.service

### Frontend

The frontend is the part of the software that gives visualization and interactivity of the data processed by backend to show it to the user in a friendly manner.

Prepare a virtual environment to install the particular packages for the frontend:

    virtualenv /srv/frontend_proj_env
    source /srv/frontend_proj_env/bin/activate

Get the source and install its particular dependencies:

    git clone https://gitlab.com/linguatec/linguatec-lexicon-frontend /srv/frontend_git
    pip3 install -r /srv/frontend_git/requirements.txt
    pip3 install -e /srv/frontend_git/

Create and initialize the project (frontend does not require database nor migration):

    cd /srv
    django-admin startproject frontend_proj --template=/srv/frontend_git/linguatec_lexicon_frontend/conf/project_template_frontend
    cd frontend_proj
    python3 manage.py collectstatic
    chown www-data: /srv/frontend_proj

To connect frontend to backend add the line `LINGUATEC_LEXICON_API_URL = 'http://api.example.com/'` in `/srv/frontend_proj/frontend_proj/settings.py`

#### Web server

The web server component of the frontend is responsible of showing example.com

Save [uwsgi_params](nginx_uwsgi_params) in `/srv/frontend_proj/uwsgi_params` and [frontend-site.conf](nginx_frontend-site.conf) in `/etc/nginx/sites-available/frontend-site.conf`

Then enable frontend site:

    ln -s /etc/nginx/sites-available/frontend-site.conf /etc/nginx/sites-enabled/frontend-site.conf

And reload nginx:

    service nginx reload

#### WGSI

The wsgi component of the frontend is responsible of making a bridge between the python code and the web server.

Create the directory if it does not exist:

    mkdir -p /etc/uwsgi

Save [frontend-site.ini](uwsgi_frontend-site.ini) in `/etc/uwsgi/frontend-site.ini`. Configure `uwsgi.service` for systemd saving [systemd_uwsgi_frontend-site.service](systemd_uwsgi_frontend-site.service) in `/etc/systemd/system/uwsgi-frontend-site.service`

Enable service on boot:

    systemctl enable uwsgi-frontend.service

Start it now:

    systemctl start uwsgi-frontend.service

## Maintenance

Note: after the `git pull` you probably would like to go to a specific git tag or git commit with the `git checkout` command

### Frontend

Update frontend repository:

    source /srv/frontend_proj_env/bin/activate
    cd /srv/frontend_git
    git pull
    python3 manage.py collectstatic

Python code changed, uwsgi service must be reloaded:

    systemctl reload uwsgi-frontend.service

### Backend

Update backend repository:

    source /srv/backend_proj_env/bin/activate
    cd /srv/backend_git
    git pull
    python3 manage.py migrate
    python3 manage.py collectstatic

Python code changed, uwsgi service must be reloaded:

    systemctl reload uwsgi-backend.service
