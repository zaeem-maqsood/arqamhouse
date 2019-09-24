import datetime
import re

from django import forms

from .models import House
from core.constants import days, months, years, provinces
from cities_light.models import City, Region, Country



class AddUserToHouse(forms.Form):

	email = forms.EmailField(required=False, widget=forms.EmailInput(
		attrs={"class": "form-control m-input", "placeholder": "Email", "autocomplete": "off", "required": False}))


class HouseChangeForm(forms.Form):

	
	def __init__(self, house_users, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["house_select"] = forms.ModelChoiceField(queryset=house_users, empty_label=None, widget=forms.Select(
			attrs={"class": "form-control m-input", "onchange": "changeHouse(this)"}))
		self.fields["house_select"].label_from_instance = lambda obj: "%s" % obj.house.name



class HouseUpdateForm(forms.ModelForm):


	class Meta:
		model = House
		fields = [
			"name",
			"region",
			"city"
		]

		widgets = {
                    "name": forms.TextInput(
                        attrs={
                            "class": "form-control m-input",
							"placeholder": "i.e. Arqam House",
                            "required": True
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
		
		cleaned_data = super(HouseUpdateForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError(
				"Please Enter A Name With More Than 2 Characters")
		return cleaned_data


class HouseForm(forms.ModelForm):

	agree = forms.BooleanField(widget=forms.CheckboxInput)

	class Meta:
		model = House
		fields = [
			"name",
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



	def clean(self, *args, **kwargs):
		cleaned_data = super(HouseForm, self).clean(*args, **kwargs)
		name = self.cleaned_data.get("name")

		if len(name) <= 3:
			raise forms.ValidationError("Please Enter A Name With More Than 2 Characters")

		checker_string = name.replace(" ", "")
		if not checker_string.isalnum():
			raise forms.ValidationError("No Special Characters Please")
		return cleaned_data
