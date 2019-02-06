# This is an example test settings file for use with the Django test suite.
#
# The 'sqlite3' backend requires only the ENGINE setting (an in-
# memory database will be used). All other backends will require a
# NAME and potentially authentication information. See the
# following section in the docs for more information:
#
# https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/
#
# The different databases that Django supports behave differently in certain
# situations, so it is recommended to run the test suite against as many
# database backends as possible.  You may want to create a separate settings
# file for each of the backends you test against.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
    'other': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

SECRET_KEY = "django_tests_secret_key"

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


"""
settings.configure(
    DEBUG_PROPAGATE_EXCEPTIONS=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    SITE_ID=1,
    SECRET_KEY='not very secret in tests',
    USE_I18N=True,
    USE_L10N=True,
    STATIC_URL='/static/',
    ROOT_URLCONF='tests.urls',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                "debug": True,  # We want template errors to raise
            }
        },
    ],
    MIDDLEWARE=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    INSTALLED_APPS=(
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'rest_framework',
        'linguatec_lexicon',
        'tests',
    ),
)

if config.getoption('--no-pkgroot'):
    sys.path.pop(0)

    # import linguatec_lexicon before pytest re-adds the package root directory.
    import linguatec_lexicon
    package_dir = os.path.join(os.getcwd(), 'linguatec_lexicon')
    assert not linguatec_lexicon.__file__.startswith(package_dir)

# Manifest storage will raise an exception if static files are not present (ie, a packaging failure).
if config.getoption('--staticfiles'):
    import linguatec_lexicon
    settings.STATIC_ROOT = os.path.join(os.path.dirname(linguatec_lexicon.__file__), 'static-root')
    settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

django.setup()

if config.getoption('--staticfiles'):
    management.call_command('collectstatic', verbosity=0, interactive=False)
"""
