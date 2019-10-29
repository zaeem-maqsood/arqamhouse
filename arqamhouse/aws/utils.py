from storages.backends.s3boto3 import S3Boto3Storage

# StaticRootS3BotoStorage = lambda: S3Boto3Storage(location='static')
# MediaRootS3BotoStorage  = lambda: S3Boto3Storage(location='media')


class StaticStorage(S3Boto3Storage):
    location = 'static'

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

class PrivateMediaStorage(S3Boto3Storage):
    location = 'media/private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
