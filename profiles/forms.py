from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from cities_light.models import City, Region, Country

from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget, PhoneNumberPrefixWidget
from django.contrib.auth.password_validation import validate_password



class ProfileChangePasswordForm(forms.Form):

	password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Enter Password', "autocomplete": "off"}))


	def clean_password(self):
		password = self.cleaned_data.get('password')
		if len(password) < 8:
			raise forms.ValidationError('Please choose a password greater than 8 chracters')

		if validate_password(password):
			raise forms.ValidationError('Please choose another password')
		return password



class LoginForm(forms.Form):

	email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email"}))
	password = forms.CharField(required=True, strip=True, widget=forms.PasswordInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Password"}))




class ProfileUpdateForm(forms.ModelForm):

	class Meta():
		model = Profile
		fields = [
			"name",
			"picture",
			"region",
			"city"
		]

		widgets = {
				"name": forms.TextInput(
					attrs={
						"class": "form-control m-input",
						"placeholder": "Name",
										"required": True
					}
				),

				"picture": forms.FileInput(
					attrs={
						"onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
						"class": "form-control m-input dropzone",
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
			}

	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['city'].empty_label = "City"
		self.fields['region'].empty_label = "Region"

		self.fields['region'].queryset = self.instance.country.region_set.order_by('name')
		self.fields['city'].queryset = self.instance.region.city_set.order_by('name')

		self.fields["region"].label_from_instance = lambda obj: "%s" % obj.name
		self.fields["city"].label_from_instance = lambda obj: "%s" % obj.name

	def clean_picture(self):
		picture = self.cleaned_data.get('picture')
		if picture:
			image_extensions = ['.jpg', '.png', '.JPG', '.PNG', '.JPEG', '.jpeg']
			error = True
			for extension in image_extensions:
				if picture.name.lower().endswith(extension) or picture.name != self.instance.slug:
					error = False

			if error:
				raise forms.ValidationError('Only .jpg .png or .jpeg files are accepted.')
			return logo
		else:
			return logo

	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileUpdateForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError(
				"Please Enter A Name With More Than 2 Characters")
		return cleaned_data




class ProfileAlreadyExistsForm(forms.ModelForm):

	email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email", "autocomplete": "off"}))
	password1 = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Enter Password', "autocomplete": "off"}))
	password2 = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Enter Password Again', "autocomplete": "off"}))
	agree = forms.BooleanField(widget=forms.CheckboxInput)

	class Meta():
		model = Profile
		fields = [
			"name",
			"email",
			"phone",
			"picture",
			"region",
			"city"
		]


		widgets = {
				"name": forms.TextInput(
					attrs={
						"class":"validate-required",
						"placeholder":"Name",
						"required": True
					}
				),
				"picture": forms.FileInput(
					attrs={
						"onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
						"class": "validate-required",
					}
				),
				"phone": PhoneNumberPrefixWidget(
                        attrs={
                            "required": True,
                            "class": "validate-required",
							"placeholder": "1234567890",
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
			}


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['city'].empty_label = None
		self.fields['region'].empty_label = None

		self.fields['city'].queryset = City.objects.all()
		self.fields['region'].queryset = Region.objects.all()

		self.fields['region'].initial = Region.objects.get(name="Ontario")
		self.fields['city'].initial = City.objects.get(name="Toronto")

		self.fields["region"].label_from_instance = lambda obj: "%s" % obj.name
		self.fields["city"].label_from_instance = lambda obj: "%s" % obj.name



	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileAlreadyExistsForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 3 Characters")
		return cleaned_data


class ProfileVerifcationForm(forms.Form):

	verification_number = forms.IntegerField(required=True, widget=forms. NumberInput(
		attrs={"required": True, "class": "validate-required", "placeholder": "Code"}))


class ProfileChangePhoneForm(forms.Form):

	phone = forms.CharField(required=True, widget=PhoneNumberPrefixWidget(
		attrs={"required": True, "class": "validate-required", "placeholder": "1234567890"}))

	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileChangePhoneForm, self).clean(*args, **kwargs)
		
		phone = self.cleaned_data.get("phone")
		print(str(phone))
		if len(str(phone)) > 13:
			raise forms.ValidationError("Please Enter A phone number with only 10 digits")
		return cleaned_data



class ProfileForm(UserCreationForm):

	email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email", "autocomplete": "off"}))
	password1 = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Enter Password', "autocomplete": "off"}))
	password2 = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Enter Password Again', "autocomplete": "off"}))
	agree = forms.BooleanField(widget=forms.CheckboxInput)

	class Meta(UserCreationForm):
		model = Profile
		fields = [
			"name",
			"email",
			"phone",
			"picture",
			"region",
			"city"
		]


		widgets = {
				"name": forms.TextInput(
					attrs={
						"class":"validate-required",
						"placeholder":"Full Name",
						"required": True
					}
				),
				"phone": PhoneNumberPrefixWidget(
                        attrs={
                            "required": True,
                            "class": "validate-required",
							"placeholder": "1234567890",
                        }
                    ),
				"picture": forms.FileInput(
					attrs={
						"onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
						"class": "",
						"style": "background: #ffffff;border: 0px;"
					}
				),
				"region": forms.Select(
						attrs={
							"required" : True,
							"class":"validate-required",
							"onchange": "cityChange(this);"
						},
					),
				"city": forms.Select(
						attrs={
							"required" : True,
							"class":"validate-required",
						}
					),
			}


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['city'].empty_label = None
		self.fields['region'].empty_label = None

		self.fields['city'].queryset = City.objects.all()
		self.fields['region'].queryset = Region.objects.all()

		self.fields['region'].initial = Region.objects.get(name="Ontario")
		self.fields['city'].initial = City.objects.get(name="Toronto")

		self.fields["region"].label_from_instance = lambda obj: "%s" % obj.name
		self.fields["city"].label_from_instance = lambda obj: "%s" % obj.name



	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 3 Characters")
		return cleaned_data








