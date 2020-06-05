from django import template
from django.conf import settings

from donations.models import Donation, DonationType
from django.db.models import Sum

import boto3
from botocore.client import Config

register = template.Library()


@register.simple_tag
def get_total_donation_amount(donation_type):
    total_donations = Donation.objects.filter(donation_type=donation_type).aggregate(Sum('amount'))["amount__sum"]
    print(total_donations)
    return total_donations



@register.simple_tag
def get_last_donor(donation_type):
    last_donor = Donation.objects.filter(donation_type=donation_type).order_by("-created_at").first()
    print(last_donor)
    return last_donor



@register.simple_tag
def get_archive_url(event_live_archive):
    from urllib.parse import unquote
    s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    response = s3_client.generate_presigned_url('get_object', Params={
        'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': event_live_archive.archive_location}, ExpiresIn=3600)
    # print(unquote(response))
    return response


    
    
