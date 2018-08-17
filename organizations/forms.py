import datetime
import re

from django import forms

from .models import Organization
from core.constants import days, months, years, provinces


class ConnectIndividualVerificationForm(forms.Form):
	first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-first-name', 'placeholder': 'Maryam'}))
	last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-last-name', 'placeholder': 'Ahmed'}))
	primary_email = forms.EmailField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-email', 'placeholder': 'maryam_ahmed@arqamhouse.com'}))
	city = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-city', 'placeholder': 'Toronto'}))
	line_1 = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-street-address1', 'placeholder': '123 Main Street'}))
	postal_code = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-zip', 'placeholder': 'M1P 5J5'}))
	province = forms.ChoiceField(required=True, choices=provinces, initial='Ontario', widget=forms.Select(attrs={'class': 'form-control m-input inp-state'}))
	dob_day = forms.ChoiceField(required=True, choices=days, widget=forms.Select(attrs={'class': 'form-control m-input inp-dob-day'}))
	dob_month = forms.ChoiceField(required=True, choices=months, widget=forms.Select(attrs={'class': 'form-control m-input inp-dob-month'}))
	dob_year = forms.ChoiceField(required=True, choices=years, initial='1995', widget=forms.Select(attrs={'class': 'form-control m-input inp-dob-year'}))
	personal_id_number = forms.CharField(max_length=9, min_length=9, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input inp-personal-id', 'placeholder': '123456789'}))
	front_side_drivers_license = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={'name': 'front-side-upload', 'onchange': "document.getElementById('front-side-pic').src = window.URL.createObjectURL(this.files[0])" }))
	back_side_drivers_license = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={'name': 'back-side-upload', 'onchange': "document.getElementById('back-side-pic').src = window.URL.createObjectURL(this.files[0])"}))

	def clean_postal_code(self, *args, **kwargs):
		postal_code = self.cleaned_data.get("postal_code")
		zipCode = re.compile(r"\s*(\w\d\s*){3}\s*")
		if zipCode.match(postal_code):
			raise forms.ValidationError("Please enter a valid postal code")
		return postal_code

	def clean_personal_id_number(self, *args, **kwargs):
		personal_id_number = self.cleaned_data.get("personal_id_number")
		personal_id_number = personal_id_number.strip()
		try:
			personal_id_number = int(personal_id_number)
		except:
			raise forms.ValidationError("Please enter a valid SIN number")
		return personal_id_number

	def clean_string(self, string):
		return any(char.isdigit() for char in string)

	def clean_city(self, *args, **kwargs):
		city = self.cleaned_data.get("city")
		result = self.clean_string(city)
		if result:
			raise forms.ValidationError("Please enter a valid city.")
		return city.strip()

	def clean_first_name(self, *args, **kwargs):
		first_name = self.cleaned_data.get("first_name")
		result = self.clean_string(first_name)
		if result:
			raise forms.ValidationError("Your name has a number in it? That's Weird.")
		return first_name

	def clean_last_name(self, *args, **kwargs):
		last_name = self.cleaned_data.get("last_name")
		result = self.clean_string(last_name)
		if result:
			raise forms.ValidationError("Your name has a number in it? That's Weird.")
		return last_name

	def clean(self, *args, **kwargs):
		cleaned_data = super(ConnectIndividualVerificationForm, self).clean(*args, **kwargs)
		dob_day = self.cleaned_data.get("dob_day")
		dob_month = self.cleaned_data.get("dob_month")
		dob_year = self.cleaned_data.get("dob_year")

		print("is it coming here?")
		try:
			dob_date = datetime.datetime(year=int(dob_year), month=int(dob_month), day=int(dob_day))
			print(dob_date)
		except Exception as e:
			print(e)
			raise forms.ValidationError("Please Enter A Valide Date of Birth")
		return cleaned_data


class ConnectCompanyVerificationForm(ConnectIndividualVerificationForm):
	business_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input', 'placeholder': 'Arqam House'}))
	business_number = forms.CharField(max_length=15, min_length=9, required=True, widget=forms.TextInput(attrs={'class': 'form-control m-input', 'placeholder': '123456789RC001'}))

	def clean_business_number(self, *args, **kwargs):
		business_number = self.cleaned_data.get("business_number")
		business_number = business_number.strip()
		return business_number


class OrganizationAndUserCreateForm(forms.ModelForm):

	email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'validate-required', 'placeholder': 'Email'}))
	password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Password'}))
	agree = forms.BooleanField(widget=forms.CheckboxInput)
	users_name = forms.CharField(max_length=70, required=True, widget=forms.TextInput(attrs={'class': 'validate-required', 'placeholder': 'Your Name'}))

	class Meta:
		model = Organization
		fields = [
			"name",
		]


		widgets = {
			"name": forms.TextInput(
					attrs={
						"class":"validate-required",
						"placeholder":"Organization Name",
						"required": True
					}
				),
			}


	def clean(self, *args, **kwargs):
		cleaned_data = super(OrganizationAndUserCreateForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 2 Characters")
		return cleaned_data


















