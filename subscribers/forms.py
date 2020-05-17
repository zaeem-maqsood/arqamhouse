from django import forms
from .models import Subscriber, Campaign

from django.conf import settings

import boto3
from botocore.client import Config

from froala_editor.widgets import FroalaEditor


class AddSubscriberForm(forms.Form):

    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={"class": "form-control m-input", "placeholder": "Subscriber Name"}), required=True)
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control m-input", "placeholder": "email@domain.com"}), required=True)
    agree = forms.BooleanField(widget=forms.CheckboxInput)




class GenericCampaignForm(forms.ModelForm):

    def __init__(self, house, *args, **kwargs):
        super(GenericCampaignForm, self).__init__(*args, **kwargs)

        s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        response = s3_client.generate_presigned_url('get_object', Params={
                                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f'media/uploads/froala_editor/images/{house.slug}'}, ExpiresIn=3600)

        self.fields["content"] = forms.CharField(required=True, widget=FroalaEditor(options={
            'toolbarInline': False, 'attribution': False, 'tableStyles': 'table', 'pastePlain': True, 'useClasses': False, 'charCounterMax': 2000, 'imageManagerLoadURL': response}, house=house))

    
    test_email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control m-input", "placeholder": "email@domain.com"}), required=False)

    class Meta:
        model = Campaign
        fields = [
            "name", "subject", "content"
        ]


        widgets = {

                "name": forms.TextInput(
                    attrs={
                        "class":"form-control m-input message",
                        "placeholder":"My Campaign's Name",
                        "required": True,
                        "maxlength": '100',
                    }
                ),

                "subject": forms.TextInput(
                        attrs={
                            "class":"form-control m-input",
                            "placeholder":"Subject",
                        }
                    ),
            }
