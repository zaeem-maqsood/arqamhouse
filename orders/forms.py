from django import forms
from .models import LineOrder


class MessageToRecipient(forms.ModelForm):

    class Meta:
        model = LineOrder
        fields = [
            "message_to_recipient",
        ]

        widgets = {

            "message_to_recipient": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "maxlength": '280',
                }
            ),
        }
