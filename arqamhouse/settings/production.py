from .base import *

DEBUG = True

ALLOWED_HOSTS = ['arqam.herokuapp.com', 'arqamhouse.com', 'www.arqamhouse.com' ]

STRIPE_SECRET_KEY = 'sk_live_4FvrAHAiKVjvUYouYDUAuT63'
STRIPE_PUBLIC_KEY = 'pk_live_HV9p4w8uuKQelYHckqDC1m0d'


DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
# del DATABASES['default']['OPTIONS']['sslmode']
# django_heroku.settings(locals())
SECURE_SSL_REDIRECT = True