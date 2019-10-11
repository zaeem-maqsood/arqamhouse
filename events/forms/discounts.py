
from django import forms
from events.models import EventDiscount


class DiscountForm(forms.ModelForm):

    class Meta:
        model = EventDiscount
        fields = [
            "code",
            "fixed_amount",
            "percentage_amount",
            "total_uses",
            "start",
            "end",
        ]

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "LOVEARQAMHOUSE",
                    "required": True
                }
            ),
            "fixed_amount": forms.NumberInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "10.00",
                    "min": "1.00"
                }
            ),
            "percentage_amount": forms.NumberInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "40",
                }
            ),
            "total_uses": forms.NumberInput(
                attrs={
                    "class": "form-control m-input",
                    "placeholder": "100",
                }
            ),
        }


    def clean(self, *args, **kwargs):

        cleaned_data = super(DiscountForm, self).clean(*args, **kwargs)
        code = self.cleaned_data.get("code")

        if len(code) <= 3 or len(code) >= 20 :
            raise forms.ValidationError(
                "Please enter a code with more than 3 characters and less than 20 characters")

        return cleaned_data
