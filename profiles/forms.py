from django import forms
from .models import Profile
from cities_light.models import City, Region, Country



class LoginForm(forms.Form):

	email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email"}))
	password = forms.CharField(required=True, strip=True, widget=forms.PasswordInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Password"}))




class ProfileForm(forms.ModelForm):

	password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'validate-required', 'placeholder': 'Password'}))
	agree = forms.BooleanField(widget=forms.CheckboxInput)

	class Meta:
		model = Profile
		fields = [
			"name",
			"email",
			"country",
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
				"email": forms.TextInput(
					attrs={
						"class":"validate-required",
						"placeholder":"Email",
						"required": True
					}
				),
				"country": forms.Select(
						attrs={
							"required" : True,
							"class":"validate-required",
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

		self.fields['country'].empty_label = "Country"
		self.fields['city'].empty_label = "City"
		self.fields['region'].empty_label = "Region"

		self.fields['city'].queryset = City.objects.all()
		self.fields['region'].queryset = Region.objects.all()

		if 'country' in self.data:
			try:
				country_id = int(self.data.get('country'))
				region_id = int(self.data.get('region'))
				self.fields['region'].queryset = Region.objects.filter(country_id=country_id).order_by('name')
				self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by('name')
			except (ValueError, TypeError):
				pass  # invalid input from the client; ignore and fallback to empty City queryset

		elif self.instance.pk:
			self.fields['region'].queryset = self.instance.country.region_set.order_by('name')
			self.fields['city'].queryset = self.instance.country.city_set.order_by('name')



	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 2 Characters")
		return cleaned_data








