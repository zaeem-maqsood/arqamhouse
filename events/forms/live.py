from .base import *
from events.models import EventLiveBroadcast


class BroadcastFacebookForm(forms.ModelForm):

    class Meta:
        model = EventLiveBroadcast
        fields = [
            "name", "facebook_url", "stream_key",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "My Facebook Stream",
                    "required": True,
                    "maxlength": '100',
                }
            ),

            "facebook_url": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "rtmps://--------------",
                    "required": True,
                    "maxlength": '200',
                }
            ),

            "stream_key": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "XXXXXXXXXXXXXXXXXXXX",
                    "required": True,
                    "maxlength": '200',
                }
            ),

        }


class BroadcastYoutubeForm(forms.ModelForm):

    class Meta:
        model = EventLiveBroadcast
        fields = [
            "name", "youtube_url", "stream_key",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "My Youtube Stream",
                    "required": True,
                    "maxlength": '100',
                }
            ),

            "youtube_url": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "rtmps://--------------",
                    "required": True,
                    "maxlength": '200',
                }
            ),

            "stream_key": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "XXXXXXXXXXXXXXXXXXXX",
                    "required": True,
                    "maxlength": '200',
                }
            ),

        }
