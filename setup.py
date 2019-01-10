import os

from setuptools import setup, find_packages


# TODO EXCLUDE_FROM_PACKAGES when adding project template
# see https://github.com/django/django/blob/master/setup.py#L55


# Dynamically calculate the version
version = __import__('linguatec_lexicon').get_version()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="linguatec-lexicon",
    version=version,
    url = 'https://gitlab.com/slamora/linguatec-lexicon/',
    author = 'Santiago Lamora',
    author_email='santiago@ribaguifi.com',
    description = ('An online bilingual dictionary based on Django.'),
    long_description=read('README.md'),
    license = 'AGPLv3 License',
    packages=find_packages(),
    zip_safe=False,
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Text Processing :: Linguistic',
    ],
)