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
            

        self.fields["content"] = forms.CharField(required=True, widget=ArqamFroalaEditor(options={
            'toolbarInline': False, 'attribution': False, 'tableStyles': 'table', 'pastePlain': True, 'useClasses': False, 'charCounterMax': 2000}, house=house))

    
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
