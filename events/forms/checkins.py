from .base import *

from events.models import Checkin


class CheckinForm(forms.ModelForm):

    class Meta:
        model = Checkin
        fields = [
            "name",
            "exclusive"
        ]

        widgets = {

                    "name": forms.TextInput(
                        attrs={
                            "class": "form-control m-input",
                            "placeholder": "Front Door Check-In",
                            "required": True
                        }
                    ),

                    "exclusive": forms.CheckboxInput(
                        attrs={
                        }
                    ),
                }
