from .base import *

DEBUG = True

ALLOWED_HOSTS = ['arqam.herokuapp.com', 'arqamhouse.com', 'www.arqamhouse.com' ]


# Test Keys
STRIPE_SECRET_KEY = 'sk_test_4o8iCn4HF5nUwtaVsnc3ysRh'
STRIPE_PUBLIC_KEY = 'pk_test_kqPiLNskd3LohLMfI49hnwzf'


# Production Keys
# STRIPE_SECRET_KEY = 'sk_live_4FvrAHAiKVjvUYouYDUAuT63'
# STRIPE_PUBLIC_KEY = 'pk_live_HV9p4w8uuKQelYHckqDC1m0d'


DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

SECURE_SSL_REDIRECT = True
