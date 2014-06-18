# load the mySociety config from its special file

import yaml
from .paths import *

config = yaml.load(open(os.path.join(PROJECT_ROOT, 'conf', 'general.yml')))

DEBUG = bool(int(config.get('STAGING')))
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config.get('SAYIT_PHILADELPHIA_DB_NAME'),
        'USER': config.get('SAYIT_PHILADELPHIA_DB_USER'),
        'PASSWORD': config.get('SAYIT_PHILADELPHIA_DB_PASS'),
        'HOST': config.get('SAYIT_PHILADELPHIA_DB_HOST'),
        'PORT': config.get('SAYIT_PHILADELPHIA_DB_PORT'),
    }
}

TIME_ZONE = config.get('TIME_ZONE')
SECRET_KEY = config.get('DJANGO_SECRET_KEY')
GOOGLE_ANALYTICS_ACCOUNT = config.get('GOOGLE_ANALYTICS_ACCOUNT')
ALLOWED_HOSTS = config.get('ALLOWED_HOSTS', [])
