from .base import *
from events.models import Event, Ticket, EventDiscount



class TicketsToCartForm(forms.Form):


	def __init__(self, event, *args, **kwargs):
		
		print(event)
		super(TicketsToCartForm, self).__init__(*args, **kwargs)

		tickets = Ticket.objects.filter(event=event)

		if EventDiscount.objects.filter(event=event).exists():
			self.fields["discount_code"] = forms.CharField(widget=forms.TextInput(attrs={"placeholder": 'Discount Code'}), required=False, max_length=20, min_length=3, strip=True)
		
		for ticket in tickets:
			min_amount = int(ticket.min_amount)
			max_amount = int(ticket.max_amount) + 1

			second_list = []
			if min_amount != 0:
				second_list.append(["0", "0"])

			for count in range(min_amount, max_amount):
				first_list = []
				for x in range(2):
					first_list.append(str(count))
				second_list.append(tuple(first_list))
			
			if ticket.donation:
				self.fields["%s_donation" % (ticket.id)] = forms.DecimalField(label=str(ticket.title), widget=forms.NumberInput(attrs={"placeholder": '10.00', 'min': '1.00', 'max':'1000.00', 'oninput': 'validity.valid||(value=value.replace(/\D+/g, ''))', 'step':'0.01'}), decimal_places=2, required=False)

			self.fields["%s" % (ticket.id)] = forms.ChoiceField(label=str(ticket.title), widget=forms.Select(), choices=second_list, required=False)

		
