import datetime
import re

from django import forms

from .models import House, HouseDirector, HouseUser
from core.constants import days, months, years, provinces
from cities_light.models import City, Region, Country

from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget, PhoneNumberPrefixWidget



class HouseContactForm(forms.Form):

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email"}))
    name = forms.CharField(required=True, strip=True, widget=forms.TextInput(attrs={"required": True, "class": "validate-required", "placeholder": "Name"}))
    message = forms.CharField(required=True, strip=True, widget=forms.Textarea(attrs={"required": True, "class": "validate-required", "placeholder": "Message"}))


class HouseLogoForm(forms.ModelForm):

    class Meta:
        model = House
        fields = [
            "logo",
        ]


        widgets = {

            "logo": forms.FileInput(
                    attrs={
                        "onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
                        "class": "form-control m-input",
                    }
                ),
            }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            image_extensions = ['.jpg', '.png', '.JPG', '.PNG', '.JPEG', '.jpeg']
            error = True
            for extension in image_extensions:
                if logo.name.lower().endswith(extension) or logo.name != self.instance.slug:
                    error = False

            if error:
                raise forms.ValidationError('Only .jpg .png or .jpeg files are accepted.')
            return logo
        else:
            return logo



class HouseUserOptionsForm(forms.ModelForm):

    class Meta:
        model = HouseUser
        fields = [
            "order_confirmations",
            "ticket_sales"
        ]


        widgets = {
            "order_confirmations": forms.CheckboxInput(
                attrs={
                    "class": "form-control m-input",
                }
            ),
            "ticket_sales": forms.CheckboxInput(
                attrs={
                    "class": "form-control m-input",
                }
            ),
        }






class HouseDirectorForm(forms.ModelForm):
    
    class Meta:
        model = HouseDirector
        fields = [
            "dob_year",
            "dob_month",
            "dob_day",
            "first_name",
            "last_name",
            "front_id",
            "back_id",
        ]

        widgets = {
                    "dob_year": forms.NumberInput(
                        attrs={
                            "class": "form-control m-input",
                            "placeholder": "Year",
                            "required": True,
                            "max": "2010",
                            "min": "1950",
                        }
                    ),
                    "dob_month": forms.NumberInput(
                        attrs={
                            "required": True,
                            "placeholder": "Month",
                            "class": "form-control m-input",
                            "min": "1",
                            "max": "12"
                        }
                    ),
                    "dob_day": forms.NumberInput(
                        attrs={
                            "required": True,
                            "placeholder": "Day",
                            "class": "form-control m-input",
                            "min": "1",
                            "max": "31"
                        }
                    ),
                    "first_name": forms.TextInput(
                        attrs={
                            "required": True,
                            "placeholder": "First Name",
                            "class": "form-control m-input",
                        }
                    ),
                    "last_name": forms.TextInput(
                        attrs={
                            "required": True,
                            "placeholder": "Last Name",
                            "class": "form-control m-input",
                        }
                    ),
                    "front_id": forms.FileInput(
                        attrs={
                            "required": True,
                            "class": "form-control m-input",
                        }
                    ),
                    "back_id": forms.FileInput(
                        attrs={
                            "required": True,
                            "class": "form-control m-input",
                        }
                    ),
                }

    


class HouseVerificationForm(forms.ModelForm):

    class Meta:
        model = House
        fields = [
            "tax_id",
            "business_number",
            "charitable_registration_number",
            "legal_name",
            "region",
            "city",
            "address",
            "postal_code",
        ]

        widgets = {
                    "legal_name": forms.TextInput(
                        attrs={
                            "class": "form-control m-input",
                             "placeholder": "Legal Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),
                    "business_number": forms.TextInput(
                        attrs={
                            "class": "form-control m-input",
                             "placeholder": "123456789RT0001",
                            "required": False,
                            "maxlength": '15',
                        }
                    ),
                    "charitable_registration_number": forms.TextInput(
                        attrs={
                            "class": "form-control m-input",
                             "placeholder": "123456789RR0001",
                            "required": False,
                            "maxlength": '15',
                        }
                    ),
                    "tax_id": forms.NumberInput(
                        attrs={
                            "required": False,
                            "placeholder": "12345678",
                            "class": "form-control m-input",
                            "min": "1",
                            "max": "99999999",
                            "step": "1"
                        }
                    ),
                    "region": forms.Select(
                        attrs={
                            "required": True,
                            "class": "form-control m-input",
                        }
                    ),
                    "city": forms.Select(
                        attrs={
                            "required": True,
                            "class": "form-control m-input",
                        }
                    ),
                    "address": forms.TextInput(
                        attrs={
                            "id": "autocomplete",
                            "required": True,
                            "class": "form-control m-input",
                        }
                    ),
                    "postal_code": forms.TextInput(
                        attrs={
                            "required": True,
                            "class": "form-control m-input",
                        }
                    ),
                }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['city'].empty_label = None
        self.fields['region'].empty_label = None

        self.fields['city'].queryset = City.objects.all()
        self.fields['region'].queryset = Region.objects.all()

        if self.instance.pk:
            self.fields['region'].queryset = Region.objects.filter(country=self.instance.country)
            self.fields['city'].queryset = City.objects.filter(region=self.instance.region)

            self.fields["region"].label_from_instance = lambda obj: "%s" % obj.name
            self.fields["city"].label_from_instance = lambda obj: "%s" % obj.name

    def clean(self, *args, **kwargs):
        cleaned_data = super(HouseVerificationForm, self).clean(*args, **kwargs)
        return cleaned_data

    def clean_business_number(self):
        business_number = self.cleaned_data.get('business_number')

        if self.instance.house_type == 'Business':
            if business_number:
                return business_number
            else:
                raise forms.ValidationError('Please enter the business number')
        else:
            return business_number


    def clean_tax_id(self):
        tax_id = self.cleaned_data.get('tax_id')

        if self.instance.house_type == 'Business':
            if tax_id:
                if len(str(tax_id)) != 8:
                    raise forms.ValidationError('Corporation/Tax ID number should be 8 digits long')
                return tax_id
            else:
                raise forms.ValidationError('Please enter the corporation/Tax ID number')
        else:
            return tax_id


    def clean_charitable_registration_number(self):
        charitable_registration_number = self.cleaned_data.get('charitable_registration_number')

        if self.instance.house_type == 'Nonprofit':
            if charitable_registration_number:
                if len(charitable_registration_number) != 15:
                    raise forms.ValidationError('Registration number should be 15 digits long')
                return charitable_registration_number
            else:
                raise forms.ValidationError('Please enter the corporation/Tax ID number')
        else:
            return charitable_registration_number



class AddUserToHouse(forms.Form):

    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={"class": "form-control m-input", "placeholder": "Email", "autocomplete": "off", "required": False}))


class HouseChangeForm(forms.Form):

    
    def __init__(self, house_users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["house_select"] = forms.ModelChoiceField(queryset=house_users, empty_label=None, widget=forms.Select(
            attrs={"class": "form-control m-input", "onchange": "changeHouse(this)"}))
        self.fields["house_select"].label_from_instance = lambda obj: "%s" % obj.house.name



class HouseSupportInfoForm(forms.ModelForm):


    class Meta:
        model = House
        fields = [
            "email",
            "phone",
            "website",
            "order_confirmations",
            "ticket_sales"
        ]

        widgets = {
                    "email": forms.EmailInput(
                        attrs={
                            "class": "form-control m-input",
                            "placeholder": "example@arqamhouse.com",
                            "required": True
                        }
                    ),
                    "phone": PhoneNumberPrefixWidget(
                        attrs={
                            "required": False,
                            "class": "form-control m-input",
                        }
                    ),
                    "website": forms.URLInput(
                        attrs={
                            "class": "form-control m-input",
                             "placeholder": "www.mywebsite.com",
                            "required": False
                        }
                    ),
                    "order_confirmations": forms.CheckboxInput(
                        attrs={
                            "class": "form-control m-input",
                        }
                    ),
                    "ticket_sales": forms.CheckboxInput(
                        attrs={
                            "class": "form-control m-input",
                        }
                    ),
                }


class HouseForm(forms.ModelForm):

    agree = forms.BooleanField(widget=forms.CheckboxInput)
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={"required": True, "class": "validate-required", "placeholder": "Support Email", "autocomplete": "off"}))

    class Meta:
        model = House
        fields = [
            "name",
            "email",
            "logo",
            "address",
            "region",
            "city"
        ]


        widgets = {
            "name": forms.TextInput(
                    attrs={
                        "class":"validate-required",
                        "placeholder":"i.e. Arqam House",
                        "required": True,
                        "pattern": """[^()/><\][\\\x22,;|]+""",
                    }
                ),

            "logo": forms.FileInput(
                    attrs={
                        "onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
                                            "class": "form-control m-input dropzone",
                    }
                ),

            "region": forms.Select(
                    attrs={
                        "required" : True,
                        "class":"validate-required",
                    }
                ),
            "city": forms.Select(
                    attrs={
                        "required" : True,
                        "class":"validate-required",
                    }
                ),
            "address": forms.TextInput(
                    attrs={
                        "autocomplete": "off",
                        "class": "validate-required",
                        "placeholder":"123 Main Street",
                        "id":"autocomplete",
                    }
                ),
            }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['city'].empty_label = None
        self.fields['region'].empty_label = None

        self.fields['city'].queryset = City.objects.all()
        self.fields['region'].queryset = Region.objects.all()

        self.fields["region"].label_from_instance = lambda obj: "%s" % obj.name
        self.fields["city"].label_from_instance = lambda obj: "%s" % obj.name

        if 'region' in self.data:
            try:
                country_id = int(self.data.get('country'))
                region_id = int(self.data.get('region'))
                self.fields['region'].queryset = Region.objects.filter(country_id=country_id).order_by('name')
                self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by('name')

                self.fields["region"].label_from_instance = lambda obj: "%s" % obj.name
                self.fields["city"].label_from_instance = lambda obj: "%s" % obj.name
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset

        elif self.instance.pk:
            self.fields['region'].queryset = self.instance.country.region_set.order_by('name')
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            image_extensions = ['.jpg', '.png', '.JPG', '.PNG', '.JPEG', '.jpeg']
            error = True
            for extension in image_extensions:
                if logo.name.lower().endswith(extension) or logo.name != self.instance.slug:
                    error = False

            if error:
                raise forms.ValidationError('Only .jpg .png or .jpeg files are accepted.')
            return logo
        else:
            return logo


    def clean(self, *args, **kwargs):
        cleaned_data = super(HouseForm, self).clean(*args, **kwargs)
        name = self.cleaned_data.get("name")

        if len(name) <= 3:
            raise forms.ValidationError("Please Enter A Name With More Than 2 Characters")

        checker_string = name.replace(" ", "")
        if not checker_string.isalnum():
            raise forms.ValidationError("No Special Characters Please")
        return cleaned_data
