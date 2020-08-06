
from django import forms
from postcards.models import PostCardOrder



class PostcardOrderForm(forms.ModelForm):

    def __init__(self, quantity, *args, **kwargs):
        super(PostcardOrderForm, self).__init__(*args, **kwargs)

        print(f"The quantity is {quantity}")
        
        self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class":"validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "autocomplete"}), required=False)


        for x in range(int(quantity)):
            self.fields["%s_recipient_name" % (x)] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": f"Recipient {x + 1}", "maxlength": '100', }), required=True)

            self.fields["%s_recipient_address" % (x)] = forms.CharField(label="Recipient Address", widget=forms.TextInput(
                attrs={"class": "validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": f"autocomplete{x}"}), required=True)

            self.fields["%s_recipient_postal_code" % (x)] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": "L1Z 5J5", "maxlength": '100', }), required=True)

            self.fields["%s_message_to_recipient" % (x)] = forms.CharField(widget=forms.Textarea(
                attrs={"class": "validate-required", "placeholder": "Write your personalized message for the recipient here", "maxlength": '280', "rows": 3, }), required=False)


    class Meta:
        model = PostCardOrder
        fields = [
            "name", "email", "anonymous", "postal_code"
        ]

        widgets = {

                "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Maryam Imran",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),


                "postal_code": forms.TextInput(
                    attrs={
                        "class": "validate-required",
                        "placeholder": "L1Z 5J5",
                        "required": False,
                        "maxlength": '7',
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


