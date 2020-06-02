import os

import environs

env = environs.Env()
env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SF_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("SF_DEBUG", default=False)

ALLOWED_HOSTS = env.list("SF_ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "anymail",
    "django_countries",
    "minishop",
    "registration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smokeyfeet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "smokeyfeet.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('SF_DB_NAME', 'smokeyfeet'),
        'USER': env.str('SF_DB_USER', 'smokeyfeet'),
        'PASSWORD': env.str('SF_DB_PASSWORD', ''),
        'HOST': env.str('SF_DB_HOST', '127.0.0.1'),
        'PORT': env.str('SF_DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"
DEFAULT_FROM_EMAIL = env.str("SF_DEFAULT_FROM_EMAIL")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s [%(levelname)s:%(name)s] %(message)s"}
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "django-smokeyfeet.log",
            "formatter": "simple",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
        "registration": {"handlers": ["file"], "level": "INFO", "propagate": True},
        "minishop": {"handlers": ["file"], "level": "INFO", "propagate": True},
    },
}

# Custom

ANYMAIL = {
    "MAILGUN_API_KEY": env.str("SF_MAILGUN_API_KEY", ""),
    "MAILGUN_SENDER_DOMAIN": "mg.smokeyfeet.com",
}

EMAIL_BASE_URI = "http://localhost:8000"

MOLLIE_API_KEY = env.str("SF_MOLLIE_API_KEY", "test_foobar")
