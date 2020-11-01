
from django import forms
from postcards.models import PostCardOrder, PostCardBusinessOrder
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget, PhoneNumberPrefixWidget



class PostCardBusinessOrderFormStepOne(forms.ModelForm):

    class Meta:
        model = PostCardBusinessOrder
        fields = [
            "name", "company_name", "email", "address", "street_number", "route", "locality", "administrative_area_level_1", "postal_code", "website", "phone"
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name",
                    "required": True,
                    "maxlength": '100',
                }
            ),

            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Postcard Estate",
                    "required": True,
                    "maxlength": '40',
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "someone@example.com",
                    "required": True,
                    "maxlength": '200',
                }
            ),

            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "123 Main Street",
                    "autocomplete": "off",
                    "required": True,
                    "id": "main_address"
                }
            ),

            "street_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "123",
                    "autocomplete": "off",
                    "required": True,
                    "id": "street_number"
                }
            ),

            "route": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Main Street",
                    "autocomplete": "off",
                    "required": True,
                    "id": "route"
                }
            ),


            "locality": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Toronto",
                    "autocomplete": "off",
                    "required": True,
                    "id": "locality"
                }
            ),

            "administrative_area_level_1": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ON",
                    "autocomplete": "off",
                    "required": True,
                    "id": "administrative_area_level_1",
                    "maxlength": '2',
                }
            ),


            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "L1Z 5J5",
                    "required": False,
                    "id": "postal_code",
                    "maxlength": '7',
                }
            ),


            "website": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://arqamhouse.com",
                    "required": False,
                    "id": "website",
                }
            ),

            "phone": PhoneNumberPrefixWidget(
                attrs={
                    "required": False,
                    "class": "form-control m-input",
                }
            ),

            

        }




class PostcardOrderForm(forms.ModelForm):

    def __init__(self, quantity, postcard, *args, **kwargs):
        super(PostcardOrderForm, self).__init__(*args, **kwargs)

        print(f"The quantity is {quantity}")
        
        self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "off", "placeholder": "123 Main Street", "id": "main_address"}), required=False)

        # Fields
        self.fields["street_number"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123", "id": "street_number"}), required=True)

        self.fields["route"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Main Street", "id": "route"}), required=True)

        self.fields["locality"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Toronto", "id": "locality"}), required=True)

        self.fields["administrative_area_level_1"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "ON", "id": "administrative_area_level_1", "maxlength": "2"}), required=True)

        self.fields["postal_code"] = forms.CharField(label="Address", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "L1Z 5G5", "id": "postal_code"}), required=True)

        self.fields["promo_code"] = forms.CharField(label="Promo Code", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Promo Code", "id": "promo_code"}), required=False)


        if postcard.non_profit:
            self.fields["donation"] = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "form-control m-input", "min": "0.00", "max": "100.00",
                                                                        "step": "1.00", "value": "5.00", "required": False}))
        else:
            print("No non-profit")

        



        for x in range(int(quantity)):
            self.fields["%s_recipient_name" % (x)] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": f"Recipient {x + 1}", "maxlength": '20', }), required=True)

            self.fields[f"autocomplete{x}"] = forms.CharField(label="Address", widget=forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "off", "placeholder": "123 Main Street", "id": f"autocomplete{x}"}), required=False)

            self.fields[f"street_number_{x}"] = forms.CharField(widget=forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "123", "id": f"street_number_{x}", "max": 99999}), required=True)

            self.fields[f"route_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Main Street", "id": f"route_{x}", "maxlength": "40"}), required=True)

            self.fields[f"locality_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Toronto", "id": f"locality_{x}", "maxlength": "40"}), required=True)

            self.fields[f"administrative_area_level_1_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ON", "id": f"administrative_area_level_1_{x}", "maxlength": "2"}), required=True)

            self.fields[f"postal_code_{x}"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": "L1Z 5G5", "id": f"postal_code_{x}", "maxlength": "10"}), required=True)



            self.fields["%s_message_to_recipient" % (x)] = forms.CharField(widget=forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Write your personalized message for the recipient here", "maxlength": '280', "rows": 3}), required=True)


    class Meta:
        model = PostCardOrder
        fields = [
            "name", "email", "anonymous", "postal_code"
        ]

        widgets = {

                "name": forms.TextInput(
                        attrs={
                            "class": "form-control",
                            "placeholder":"Maryam Imran",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),


                "postal_code": forms.TextInput(
                    attrs={
                        "class": "form-control",
                        "placeholder": "L1Z 5J5",
                        "required": False,
                        "maxlength": '7',
                    }
                ),

                "email": forms.EmailInput(
                        attrs={
                            "class": "form-control",
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


