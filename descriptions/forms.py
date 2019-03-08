
from django import forms

from .models import (H1Title, H2Title, H3Title, Paragraph)


class H1TitleForm(forms.ModelForm):

	order = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": "Order"}))

	class Meta:
		model = H1Title
		fields = [
			"order", "title",
		]


		widgets = {



				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"An Example of an H1 Title",
							"required": True,
							"maxlength": '100',
						}
					),
				}





class H2TitleForm(forms.ModelForm):

	order = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": "Order"}))

	class Meta:
		model = H2Title
		fields = [
			"order", "title",
		]


		widgets = {



				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"An Example of an H1 Title",
							"required": True,
							"maxlength": '100',
						}
					),
				}



class H3TitleForm(forms.ModelForm):

	order = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": "Order"}))

	class Meta:
		model = H3Title
		fields = [
			"order", "title",
		]


		widgets = {



				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"An Example of an H1 Title",
							"required": True,
							"maxlength": '100',
						}
					),
				}




class ParagraphForm(forms.ModelForm):

	order = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": "Order"}))

	class Meta:
		model = Paragraph
		fields = [
			"order", "text",
		]


		widgets = {

				"text": forms.Textarea(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"An example of paragraph text",
							"required": True,
							"rows": '5'
						}
					),
				}

				


