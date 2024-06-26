
from django import forms
from postcards.models import PostCardOrder, PostCardBusinessOrder
from orders.models import Order
from recipients.models import Recipient
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




class PostcardOrderForm(forms.Form):

    def __init__(self, quantity, postcard, profile, authenticated, *args, **kwargs):
        super(PostcardOrderForm, self).__init__(*args, **kwargs)

        self.authenticated = authenticated
        self.profile = profile
        self.quantity = quantity

        print(f"The quantity is {quantity}")

        if profile and authenticated:
            pass
        else:

            self.fields["name"] = forms.CharField(widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Full Name", "oninput": "revealPasswordField();"}), required=True, max_length=30)

            self.fields["email"] = forms.EmailField(widget=forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "someone@example.com", "oninput": "revealPasswordField();"}), required=True, max_length=200)

            self.fields["password"] = forms.CharField(max_length=100, required=False, widget=forms.PasswordInput(
                attrs={'class': 'form-control', 'placeholder': 'Password', "autocomplete": "off"}))
        
            self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "off", "placeholder": "123 Main Street", "id": "main_address", "onfocusout": "hideMainAddressOnInput();"}), required=False)

            # Fields
            self.fields["apt_number"] = forms.CharField(label="Apt Number", widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": "", "id": "apt_number"}), required=False)

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

        self.fields["anonymous"] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={"checked": False}), required=False,)
            
        self.fields["promo_code"] = forms.CharField(label="Promo Code", widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Promo Code", "id": "promo_code"}), required=False)

        self.fields["add_gift_card"] = forms.BooleanField(label="Add Gift Card", widget=forms.CheckboxInput(
            attrs={"class": "custom-control-input", "id": "gift_card_switch", "onchange": "checkGiftCard(this);"}), required=False)

        self.fields["gift_card_amount"] = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "form-control m-input", "min": "0.00", "max": "100.00",
                                                                                             "step": "1.00", "value": "5.00", "id": "id_gift_card_amount"}), required=False)


        if postcard.non_profit:
            self.fields["donation"] = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "form-control m-input", "min": "0.00", "max": "100.00",
                                                                        "step": "1.00", "value": "5.00"}), required=False)
        else:
            print("No non-profit")



        for x in range(int(quantity)):

            if authenticated:
                self.fields[f"recipient_{x}"] = forms.ModelChoiceField(queryset=Recipient.objects.filter(profile=profile).order_by("-counter"), empty_label=None)

            else:
                self.fields["%s_recipient_name" % (x)] = forms.CharField(widget=forms.TextInput(
                    attrs={"class": "form-control", "placeholder": f"Recipient {x + 1}", "maxlength": '20', }), required=True)

                self.fields[f"autocomplete{x}"] = forms.CharField(label="Address", widget=forms.TextInput(
                    attrs={"class": "form-control", "autocomplete": "off", "placeholder": "123 Main Street", "id": f"autocomplete{x}"}), required=False)

                self.fields[f"apt_number_{x}"] = forms.CharField(widget=forms.NumberInput(
                    attrs={"class": "form-control", "placeholder": "10", "id": f"recipient_apt_number_{x}", "max": 99999}), required=False)

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


    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) > 30:
            raise forms.ValidationError('Please keep your name under 30 characters long.')
        return name

    def clean(self, *args, **kwargs):
        cleaned_data = super(PostcardOrderForm, self).clean(*args, **kwargs)

        if self.profile and self.authenticated:
            pass

        else:
            
            # Name Validation
            name = self.cleaned_data.get('name')
            if len(name) > 25 or len(name) < 4:
                raise forms.ValidationError('Name must be between 4 and 25 characters.')

            # Email Validation
            email = self.cleaned_data.get('email')
            if len(email) > 300:
                raise forms.ValidationError('Please keep your email under 200 characters long.')

            # Apt number validation
            apt_number = self.cleaned_data.get("apt_number")
            if apt_number:
                if len(apt_number) > 10:
                    raise forms.ValidationError("Please keep your apt/suite number under 20 characters long.")
            
            # Street Number Validation
            street_number = self.cleaned_data.get("street_number")
            if len(street_number) > 20:
                raise forms.ValidationError("Please keep your street number under 20 characters long.")

            # Route Validation
            route = self.cleaned_data.get("route")
            if len(route) > 100:
                raise forms.ValidationError("Please keep your route under 100 characters long.")

            # Locality Validation
            locality = self.cleaned_data.get("locality")
            if len(locality) > 100:
                raise forms.ValidationError("Please keep your locality under 100 characters long.")

            # admin area 1 validation
            administrative_area_level_1 = self.cleaned_data.get("administrative_area_level_1")
            if len(administrative_area_level_1) >= 4:
                raise forms.ValidationError("Please use a 2 digit province code i.e. 'ON'.")

            # Postal Code validation
            postal_code = self.cleaned_data.get("postal_code")
            if len(postal_code) > 10:
                raise forms.ValidationError("Please keep the postal code under 10 characters long.")


            for x in range(int(self.quantity)):

                # Recipient Name Validation
                recipient_name = self.cleaned_data.get(f'{x}_recipient_name')
                if len(recipient_name) > 25 or len(recipient_name) < 4:
                    raise forms.ValidationError('Recipient name must be between 4 and 25 characters.')

                # Recipient Apt number validation
                recipient_apt_number = self.cleaned_data.get(f"apt_number_{x}")
                if recipient_apt_number:
                    if len(recipient_apt_number) > 10:
                        raise forms.ValidationError("Please keep recipient apt/suite number under 10 characters long.")

                # Recipient Street Number Validation
                recipient_street_number = self.cleaned_data.get(f"street_number_{x}")
                if len(recipient_street_number) > 10:
                    raise forms.ValidationError("Please keep recipient street number under 10 characters long.")

                # Recipient Route Validation
                recipient_route = self.cleaned_data.get(f"route_{x}")
                if len(recipient_route) > 100:
                    raise forms.ValidationError("Please keep recipient route under 100 characters long.")

                # Recipient Locality Validation
                recipient_locality = self.cleaned_data.get(f"locality_{x}")
                if len(recipient_locality) > 100:
                    raise forms.ValidationError("Please keep recipient locality under 100 characters long.")

                # Recipient admin area 1 validation
                recipient_administrative_area_level_1 = self.cleaned_data.get(f"administrative_area_level_1_{x}")
                if len(recipient_administrative_area_level_1) >= 4:
                    raise forms.ValidationError("Please use a 2 digit province code i.e. 'ON'.")

                # Recipient Postal Code validation
                recipient_postal_code = self.cleaned_data.get(f"postal_code_{x}")
                if len(recipient_postal_code) > 7:
                    raise forms.ValidationError("Please keep recipient postal code under 10 characters long.")










