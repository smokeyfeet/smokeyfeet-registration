import os

from .settings_default import *

# Django

SECRET_KEY = "local_secret"

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('SF_DB_NAME', 'smokeyfeet'),
        'USER': os.environ.get('SF_DB_USER', 'smokeyfeet'),
        'PASSWORD': os.environ.get('SF_DB_PASSWORD', ''),
        'HOST': os.environ.get('SF_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('SF_DB_PORT', '5432'),
    }
}

DEFAULT_FROM_EMAIL = 'Smokey Feet <info@smokeyfeet.com>'
EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s:%(name)s] %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django-smokeyfeet.log',
            'formatter': 'simple'
        },
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'registration': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'minishop': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Custom

ANYMAIL = {
    'MAILGUN_API_KEY': os.environ.get('MAILGUN_API_KEY', ''),
    'MAILGUN_SENDER_DOMAIN': 'mg.smokeyfeet.com',
}

EMAIL_BASE_URI = 'http://localhost:8000'

MOLLIE_API_KEY = os.environ.get('SF_MOLLIE_API_KEY', '')
