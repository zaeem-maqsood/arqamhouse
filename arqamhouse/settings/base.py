"""
Django settings for arqamhouse project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from celery.schedules import crontab
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
    'storages',
    'cities_light',
    'organizations',
    'profiles',
    'payouts',
    'events',
    'tickets',
    'questions',
    'carts',
    'orders',
    'attendees',
    'answers',
    'descriptions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arqamhouse.urls'


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


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'arqamhouse',
#         'USER': 'arqamhouse',
#         'PASSWORD': 'Ed81ae9600!',
#         'HOST': 'localhost',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)



# Django cities settings
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['fr', 'en']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['CA', 'US']
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]


# Celery stuff 
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# System wide Cron jobs using Celery 
CELERY_BEAT_SCHEDULE = {
    'hello': {
        'task': 'events.tasks.hello',
        'schedule': crontab()  # execute every minute
    }
}


# Sendgrid Email Backend
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
SENDGRID_API_KEY = "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"

# To err on the side of caution, this defaults to True, so emails sent in DEBUG mode will not be delivered,
 # unless this setting is explicitly set to False.
SENDGRID_SANDBOX_MODE_IN_DEBUG = False




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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = 'profiles:login'


STRIPE_FEE = 2.9
STRIPE_BASE_FEE = 0.30
PLATFORM_FEE = 5
PLATFORM_BASE_FEE = 0.30


# AWS_ACCESS_KEY_ID = "AKIAJLQ5COLYAR6REXEQ"
# AWS_SECRET_ACCESS_KEY = "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"



# AWS_FILE_EXPIRE = 200
# AWS_PRELOAD_METADATA = True
# AWS_QUERYSTRING_AUTH = True

# DEFAULT_FILE_STORAGE = 'arqamhouse.utils.MediaRootS3BotoStorage'
# STATICFILES_STORAGE = 'arqamhouse.utils.StaticRootS3BotoStorage'
# AWS_STORAGE_BUCKET_NAME = 'arqam-static'
# AWS_S3_REGION_NAME = 'us-west-1'

# S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
# MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
# MEDIA_ROOT = MEDIA_URL
# STATIC_URL = S3_URL + 'static/'
# ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# import datetime

# two_months = datetime.timedelta(days=61)
# date_two_months_later = datetime.date.today() + two_months
# expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

# AWS_HEADERS = { 
#     'Expires': expires,
#     'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
# }



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_DIRS = [
     os.path.join(BASE_DIR, "static"),
 ]

# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'

# STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "staticfiles")
# MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media")





