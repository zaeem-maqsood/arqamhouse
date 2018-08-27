from django import forms
from .models import Profile



class LoginForm(forms.Form):

	email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email"}))
	password = forms.CharField(required=True, strip=True, widget=forms.PasswordInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Password"}))




class ProfileForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = [
			"name",
			"email",
			"timezone",
		]


		widgets = {
				"name": forms.TextInput(
						attrs={
							"required" : True,
							"type": "text",
							"class":"form-control m-input",
						}
					),
				"email": forms.TextInput(
						attrs={
							"class":"form-control",
						}
					),
				"timezone": forms.Select(
						attrs={
							"required" : True,
							"class":"form-control m-input",
						}
					),
				"region": forms.Select(
						attrs={
							"required" : True,
							"class":"form-control m-input",
						}
					),
				"city": forms.Select(
						attrs={
							"required" : True,
							"class":"form-control m-input",
						}
					),
			}



	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 2 Characters")
		return cleaned_data








