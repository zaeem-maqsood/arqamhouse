import datetime
AWS_ACCESS_KEY_ID = "AKIAQM5VEUNBX43MNFXZ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'arqamhouse.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'arqamhouse.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'arqam'
# AWS_S3_SIGNATURE_VERSION = 's3v4'
S3DIRECT_REGION = 'us-west-2'
AWS_S3_SIGNATURE_VERSION = 's3v4'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")


AWS_HEADERS = { 
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}