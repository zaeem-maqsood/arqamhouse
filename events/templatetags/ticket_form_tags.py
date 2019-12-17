from django import template

register = template.Library()

@register.simple_tag
def get_ticket_related_form_field(form, ticket):

	for field in form:
		try:
			if int(field.name) == int(ticket.id):
				return field
			else:
				pass
		except:
			pass


@register.simple_tag
def get_ticket_related_form_field_donation(form, ticket):

	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(ticket.id):
				return field
			else:
				pass
		except:
			pass

