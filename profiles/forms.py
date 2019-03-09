from django import forms
from .models import Profile



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
			"timezone",
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
				"timezone": forms.Select(
						attrs={
							"required" : True,
							"class":"validate-required",
						}
					)
			}



	def clean(self, *args, **kwargs):
		cleaned_data = super(ProfileForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 2 Characters")
		return cleaned_data








