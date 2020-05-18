from django import forms
from .models import Subscriber, Campaign

from django.conf import settings

import boto3
from botocore.client import Config

from core.widgets import ArqamFroalaEditor


class AddSubscriberForm(forms.Form):

    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={"class": "form-control m-input", "placeholder": "Subscriber Name"}), required=True)
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control m-input", "placeholder": "email@domain.com"}), required=True)
    agree = forms.BooleanField(widget=forms.CheckboxInput)




class GenericCampaignForm(forms.ModelForm):

    def __init__(self, house, *args, **kwargs):
        super(GenericCampaignForm, self).__init__(*args, **kwargs)

        # s3_client = boto3.client('s3')
        # # for key in s3_client.list_objects(Bucket='arqam')['Contents']:
        # #     print(key['Key'])
        # for key in s3_client.list_objects(Bucket='arqam', Prefix=f'media/uploads/froala_editor/images/{house.slug}')['Contents']:
        #     print(key['Key'])

        # location_url = s3_client.list_objects(Bucket='arqam', Prefix=f'media/uploads/froala_editor/images/{house.slug}')['Contents']
        # print(location_url)
            

        self.fields["content"] = forms.CharField(required=True, widget=ArqamFroalaEditor(options={
            'toolbarInline': False, 'attribution': False, 'tableStyles': 'table', 'pastePlain': True, 'useClasses': False, 'charCounterMax': 2000, 'imageManagerLoadURL': "https://arqam.s3.ca-central-1.amazonaws.com/media/uploads/froala_editor/images/arqam-house/"}, house=house))

    
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
