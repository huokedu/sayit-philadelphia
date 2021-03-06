# Django settings for sayit_philadelphia project.

import os
from django.conf import global_settings
from .paths import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PARENT_DIR, 'sqlite.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PARENT_DIR, 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PARENT_DIR, 'collected_static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'web'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'speeches.middleware.InstanceMiddleware',
)

ROOT_URLCONF = 'sayit_philadelphia.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sayit_philadelphia.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    "django.core.context_processors.request",
    "sayit_philadelphia.context_processors.add_settings",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'haystack',
    'south',
    'pipeline',
    'django_select2',
    'django_bleach',
    'popit',
    'popolo',
    'instances',
    'speeches',
)

# Log WARN and above to stderr; ERROR and above by email when DEBUG is False.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': [ 'mail_admins', 'console' ],
            'level': 'WARN',
            'propagate': True,
        },
    }
}

# pagination related settings
PAGINATION_DEFAULT_WINDOW = 2

# Cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Now get the mySociety configuration

from .mysociety import *

# django-bleach configuration
from .bleach import *

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': DATABASES['default']['NAME'],
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Select2
AUTO_RENDER_SELECT2_STATICS = False

# Pipeline

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
# You can use e.g. 'pipeline.compressors.yui.YUICompressor' in the two
# lines below if you install YUI Compressor
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

PIPELINE_COMPILERS = (
    'pipeline_compass.compass.CompassCompiler',
)

import speeches
PIPELINE_COMPASS_ARGUMENTS = '-I %s -r zurb-foundation' % os.path.join(speeches.__path__[0], 'static')

PIPELINE_CSS = {
    'sayit-default': {
        'source_filenames': (
            'sass/project.scss',
        ),
        'output_filename': 'css/project.css',
    },
}

PIPELINE_JS = {
    'sayit-default-head': {
        'source_filenames': (
            'speeches/js/jquery.js',
        ),
        'output_filename': 'js/sayit.head.min.js',
    },
    'sayit-default': {
        'source_filenames': (
            'speeches/js/foundation/foundation.js',
            'speeches/js/foundation/foundation.dropdown.js',
            'speeches/js/speeches.js',
        ),
        'output_filename': 'js/sayit.min.js',
    },
    'sayit-player': {
        'source_filenames': (
            'speeches/mediaelement/mediaelement-and-player.js',
        ),
        'output_filename': 'js/sayit.mediaplayer.min.js',
    },
    'sayit-upload': {
        'source_filenames': (
            'speeches/js/jQuery-File-Upload/js/vendor/jquery.ui.widget.js',
            'speeches/js/jQuery-File-Upload/js/jquery.iframe-transport.js',
            'speeches/js/jQuery-File-Upload/js/jquery.fileupload.js',
        ),
        'output_filename': 'js/sayit.upload.min.js',
    },
}
