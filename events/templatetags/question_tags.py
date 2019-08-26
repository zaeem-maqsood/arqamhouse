from django import template
from events.models import EventQuestion

register = template.Library()


@register.filter(name='ticket_checked')
def ticket_checked(ticket, event_question):
	if event_question.tickets.filter(id=ticket.id):
		return "checked"
	else:
		return None