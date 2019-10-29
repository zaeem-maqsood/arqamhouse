import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

AWS_ACCESS_KEY_ID = "AKIAQM5VEUNBX43MNFXZ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = 'arqam'
AWS_S3_REGION_NAME = 'ca-central-1'

AWS_S3_CUSTOM_DOMAIN_TO_USE = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME


two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
# expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")
AWS_S3_OBJECT_PARAMETERS = {
    # 'Expires': expires,
    'CacheControl': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

STATICFILES_STORAGE = 'arqamhouse.aws.utils.StaticStorage'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN_TO_USE, 'static')

DEFAULT_FILE_STORAGE = 'arqamhouse.aws.utils.MediaStorage'
MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN_TO_USE, 'media')

PRIVATE_FILE_STORAGE = 'arqamhouse.aws.utils.PrivateMediaStorage'

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

AWS_QUERYSTRING_AUTH = True
AWS_DEFAULT_ACL = "private"


# STATICFILES_FINDERS = (           
#     'django.contrib.staticfiles.finders.FileSystemFinder',    
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# )


# AWS_PRELOAD_METADATA = False
# AWS_QUERYSTRING_AUTH = None




# STATICFILES_STORAGE = 'arqamhouse.aws.utils.StaticRootS3BotoStorage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# AWS_S3_SIGNATURE_VERSION = 's3v4'
# S3DIRECT_REGION = 'ca-central-1'

# AWS_S3_SIGNATURE_VERSION = 's3v4'
# S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
# MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
# MEDIA_ROOT = MEDIA_URL
# STATIC_URL = S3_URL + 'static/'
# ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
# AWS_DEFAULT_ACL = 'private'





