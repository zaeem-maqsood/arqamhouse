
from django import forms
from postcards.models import PostCardOrder



class PostcardOrderForm(forms.ModelForm):

    def __init__(self, quantity, *args, **kwargs):
        super(PostcardOrderForm, self).__init__(*args, **kwargs)

        print(f"The quantity is {quantity}")
        
        self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "main_address"}), required=False)

        # Fields
        self.fields["street_number"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "placeholder": "123", "id": "street_number"}), required=False)

        self.fields["route"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "placeholder": "Main Street", "id": "route"}), required=False)

        self.fields["locality"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "placeholder": "Toronto", "id": "locality"}), required=False)

        self.fields["administrative_area_level_1"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "placeholder": "ON", "id": "administrative_area_level_1"}), required=False)

        self.fields["postal_code"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "validate-required", "placeholder": "L1Z 5G5", "id": "postal_code"}), required=False)

        



        for x in range(int(quantity)):
            self.fields["%s_recipient_name" % (x)] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": f"Recipient {x + 1}", "maxlength": '100', }), required=True)

            self.fields[f"autocomplete{x}"] = forms.CharField(label="Address", widget=forms.TextInput(
                attrs={"class": "validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": f"autocomplete{x}"}), required=False)

            self.fields[f"street_number_{x}"] = forms.IntegerField(widget=forms.NumberInput(
                attrs={"class": "validate-required", "placeholder": "123", "id": f"street_number_{x}"}), required=False)

            self.fields[f"route_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": "Main Street", "id": f"route_{x}", "maxlength": "100"}), required=False)

            self.fields[f"locality_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": "Toronto", "id": f"locality_{x}", "maxlength": "100"}), required=False)

            self.fields[f"administrative_area_level_1_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": "ON", "id": f"administrative_area_level_1_{x}", "maxlength": "2"}), required=False)

            self.fields[f"postal_code_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "validate-required", "placeholder": "L1Z 5G5", "id": f"postal_code_{x}", "maxlength": "10"}), required=False)



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


