from .base import *

DEBUG = True

ALLOWED_HOSTS = ['arqam.herokuapp.com', ]

STRIPE_SECRET_KEY = 'sk_live_4FvrAHAiKVjvUYouYDUAuT63'
STRIPE_PUBLIC_KEY = 'pk_live_HV9p4w8uuKQelYHckqDC1m0d'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'jfwqdsslbabcxq',
        'HOST': 'ec2-54-235-65-224.compute-1.amazonaws.com',
        'PORT': 5432,
    }
}