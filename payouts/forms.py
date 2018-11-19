from django import forms
from .models import Event



class EventPayoutForm(forms.Form):

	def __init__(self, orders, *args, **kwargs):
		
		super(EventPayoutForm, self).__init__(*args, **kwargs)

		for order in orders:
			self.fields["%s_order" % (order.id)] = forms.BooleanField(label=str(order.name), required=False, initial=True, widget=forms.CheckboxInput(attrs={"class":"", "onclick":"myFunction()"}))

