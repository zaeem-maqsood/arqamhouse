"""
Django settings for arqamhouse project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import django_heroku
import dj_database_url
import dotenv
import os
# from celery.schedules import crontab
from arqamhouse.aws.conf import *


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1e-5=g=*(e*&%yy0atewsxk$mz#og$x@o_x!yxwvmzaecsv-r1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'django_hosts',
    'storages',
    'cities_light',
    'houses',
    'profiles',
    'payments',
    'events',
    'questions',

]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

ROOT_URLCONF = 'arqamhouse.urls'
ROOT_HOSTCONF = 'arqamhouse.hosts'
DEFAULT_HOST = 'www'


DATA_UPLOAD_MAX_NUMBER_FIELDS = 102400


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'arqamhouse.wsgi.application'


ADMINS = [('Zaeem Maqsood', 'errors@arqamhouse.com')]


# Django cities settings
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['fr', 'en']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['CA']
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]


# Celery stuff 
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# System wide Cron jobs using Celery 
# CELERY_BEAT_SCHEDULE = {
#     'hello': {
#         'task': 'events.tasks.hello',
#         'schedule': crontab()  # execute every minute
#     }
# }


# Sendgrid Email Backend

# SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
SENDGRID_API_KEY = "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"

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'Arqam House <info@arqamhouse.com>'
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

# To err on the side of caution, this defaults to True, so emails sent in DEBUG mode will not be delivered,
 # unless this setting is explicitly set to False.
SENDGRID_SANDBOX_MODE_IN_DEBUG = False


# Google Maps API
GOOGLE_MAPS_API = 'AIzaSyDtDBaUdChaO8Br25g14tY8W3bzXPtHqys'



# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Toronto'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = 'profiles:login'

AUTH_USER_MODEL = 'profiles.Profile'

AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )


STRIPE_FEE = 2.9
STRIPE_BASE_FEE = 0.30
PLATFORM_FEE = 4.0
PLATFORM_BASE_FEE = 0.30



FROALA_EDITOR_PLUGINS = ('align', 'char_counter', 'code_beautifier', 'colors', 'draggable', 'emoticons', 'font_family', 'font_size', 'inline_style', 'link', 'lists', 'paragraph_format', 'paragraph_style', 'quick_insert', 'quote', 'table',
                         'url')


FROALA_EDITOR_OPTIONS = {
    'key': 'PYC4mB3B15B11A7C4A5dxhjA-21pvpurgH3gjkD-17D2E2F2C1E4F1A1B8D7E6==',
}

