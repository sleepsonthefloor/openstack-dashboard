import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEBUG = True
TESTSERVER = 'http://testserver'
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/django-nova.db'
INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django_nova']
ROOT_URLCONF = 'django_nova.tests.urls'
TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'tests', 'templates')
)
SITE_BRANDING = 'OpenStack'
SITE_NAME = 'openstack'
NOVA_DEFAULT_ENDPOINT = 'none'
NOVA_DEFAULT_REGION = 'test'
NOVA_ACCESS_KEY = 'test'
NOVA_SECRET_KEY = 'test'
