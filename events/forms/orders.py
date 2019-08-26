from django import forms
import decimal


class RefundForm(forms.Form):

	partial_refund = forms.BooleanField(label="Partial Refund", widget=forms.CheckboxInput, required=False)
	


	def __init__(self, total, *args, **kwargs):

		super(RefundForm, self).__init__(*args, **kwargs)
		min_value = decimal.Decimal(1.00)
		max_value = decimal.Decimal(total)
		self.fields['refund_amount'] = forms.DecimalField(min_value=min_value, max_value=max_value, max_digits=6, decimal_places=2, required=False, widget=forms.NumberInput(attrs={"class":"form-control m-input", "placeholder": "2.00", "disabled": "true"}))



	def clean_partial_refund(self):
		print("DID IT EVEN CALL THIS")
		partial_refund = self.cleaned_data.get('partial_refund')
		refund_amount = self.cleaned_data.get('refund_amount')
		if partial_refund:
			if refund_amount is None or refund_amount == '':
				raise forms.ValidationError('Please enter an amount if you are doing a partial refund.')
			else:
				try:
					refund_amount = decimal.Decimal(refund_amount)
				except:
					raise forms.ValidationError('Please enter a valid amount.')
		else:
			return partial_refund