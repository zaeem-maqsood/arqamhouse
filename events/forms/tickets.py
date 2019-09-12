from django import forms

from events.models import Event, Ticket



class DonationTicketForm(forms.ModelForm):

	amount_available = forms.IntegerField(min_value=0, required=False, max_value=30000, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": '300'}))

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
							"placeholder":"Give your ticket a description here. Totally optional.",
							"rows": '3'
						}
					),
				}


	def clean_amount_available(self):
		amount_available = self.cleaned_data.get('amount_available')
		if amount_available is not None:
			if self.instance.amount_sold > amount_available:
				raise forms.ValidationError('You have already Sold %s tickets. Please choose a greater number.' % (self.instance.amount_sold))
			else:
				return amount_available

		



class FreeTicketForm(DonationTicketForm):

	min_amount = forms.IntegerField(min_value=0, max_value=10, required=False, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": '0'}))
	max_amount = forms.IntegerField(min_value=0, max_value=10, required=False, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": '10'}))

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
							"placeholder":"Give your ticket a description here. Totally optional..",
							"rows": '3'
						}
					),
				}





class PaidTicketForm(FreeTicketForm):
	
	class Meta:
		model = Ticket
		fields = [
			"title", "description", "price", "pass_fee", "min_amount", "max_amount", "amount_available"
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
							"placeholder":"Give your ticket a description here. Totally optional.",
							"rows": '3'
						}
					),

				"price": forms.NumberInput(
						attrs={
							"class":"form-control m-input",
							"min" : "1.00",
							"max": "2000.00",
							"step": "0.01",
							"value": "5.00",
							"required": True,
						}
					),

				"pass_fee": forms.CheckboxInput(
						attrs={
						}
					),

				}





