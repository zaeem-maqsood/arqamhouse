
from django import forms
from postcards.models import PostCardOrder



class PostcardOrderForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(PostcardOrderForm, self).__init__(*args, **kwargs)
        self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class":"validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "autocomplete"}), required=False)
        self.fields["recipient_address"] = forms.CharField(label="Recipient Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "autocomplete2"}), required=False)

    class Meta:
        model = PostCardOrder
        fields = [
            "name", "email", "anonymous", "message_to_recipient", "recipient_name",
            "recipient_postal_code"
        ]

        widgets = {

                "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Your loving sister, Maryam.",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                "recipient_name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "Maryam Imran",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                "recipient_postal_code": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"L1Z 5J5",
                            "required": True,
                            "maxlength": '7',
                        }
                    ),

                "message_to_recipient": forms.Textarea(
                        attrs={
                            
                            "placeholder":"Give a personalized message with your gift",
                            "required": False,
                            "maxlength": '150',
                            "rows": 2,
                        }
                    ),

                "email": forms.EmailInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "someone@example.com",
                            "required": True,
                            "maxlength": '200',
                        }
                    ),

                "anonymous": forms.CheckboxInput(
                    attrs={
                        "checked": False,
                    }
                ),
        }



    def clean_address(self):
        address = self.cleaned_data.get('address')

        if not address:
            raise forms.ValidationError('Please enter an address')
        else:
            return address


