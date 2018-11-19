from django import template
from carts.models import EventCart, EventCartItem
from questions.models import EventQuestion, AllTicketQuestionControl, TicketQuestion
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()

@register.simple_tag
def get_order_related_form_field(form, order):

	print()
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(order.id) and field.name.split('_')[1] == "order":
				print("This is the id")
				print(order.id)
				return field
			else:
				pass
		except Exception as e:
			print(e)
			pass