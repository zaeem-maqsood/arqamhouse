from django import forms

from .models import Ticket
from events.models import Event



class DonationTicketForm(forms.ModelForm):

	amount_available = forms.IntegerField(min_value=0, max_value=30000, widget=forms.NumberInput(attrs={"class":"form-control m-input"}))

	class Meta:
		model = Ticket
		fields = [
			"title", "description", "amount_available"
		]

		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"General Admission",
							"required": True,
							"maxlength": '100',
						}
					),

				"description": forms.Textarea(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Give you event a short and sweet description to hook in potential ticket buyers. Totally optional.",
							"rows": '5'
						}
					),
				}


	def clean_amount_available(self):
		amount_available = self.cleaned_data.get('amount_available')
		if self.instance.amount_sold > amount_available:
			raise forms.ValidationError('You have already Sold %s tickets. Please choose a greater number.' % (self.instance.amount_sold))
		else:
			return amount_available

		



class FreeTicketForm(DonationTicketForm):

	min_amount = forms.IntegerField(min_value=0, max_value=10, widget=forms.NumberInput(attrs={"class":"form-control m-input"}))
	max_amount = forms.IntegerField(min_value=0, max_value=10, widget=forms.NumberInput(attrs={"class":"form-control m-input"}))

	class Meta:
		model = Ticket
		fields = [
			"title", "description", "min_amount", "max_amount", "amount_available"
		]

		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"General Admission",
							"required": True,
							"maxlength": '100',
						}
					),

				"description": forms.Textarea(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Give you event a short and sweet description to hook in potential ticket buyers. Totally optional.",
							"rows": '5'
						}
					),
				}





class PaidTicketForm(FreeTicketForm):

	sale_start = forms.DateTimeField(input_formats=["%m/%d/%Y %I:%M %p"], widget=forms.DateTimeInput(attrs={"class":"form-control m-input", "placeholder":"MM/DD/YYYY 00:00 AM/PM", "required": False}))
	sale_end = forms.DateTimeField(input_formats=["%m/%d/%Y %I:%M %p"], widget=forms.DateTimeInput(attrs={"class":"form-control m-input", "placeholder":"MM/DD/YYYY 00:00 AM/PM", "required": False}))
	
	
	class Meta:
		model = Ticket
		fields = [
			"title", "description", "price", "sale_price", "sale_start", "sale_end", "pass_fee", "min_amount", "max_amount", "amount_available"
		]

		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"General Admission",
							"required": True,
							"maxlength": '100',
						}
					),

				"description": forms.Textarea(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Give you event a short and sweet description to hook in potential ticket buyers. Totally optional.",
							"rows": '5'
						}
					),

				"price": forms.NumberInput(
						attrs={
							"class":"form-control m-input",
						}
					),

				"sale_price": forms.NumberInput(
						attrs={
							"class":"form-control m-input",
							"id": "id_sale_price",
						}
					),

				"pass_fee": forms.CheckboxInput(
						attrs={
						}
					),

				}


	def __init__(self, *args, **kwargs):
		super(PaidTicketForm, self).__init__(*args, **kwargs)

		self.fields["sale_start"].required = False
		self.fields["sale_end"].required = False





