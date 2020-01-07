from django import template
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

from events.models import Attendee, Checkin, Ticket

register = template.Library()


@register.simple_tag
def check_if_checked_in(checkin, attendee):

    if checkin in attendee.checkins.all():
        return "Check-Out"
    else:
        return "Check-In"


@register.simple_tag
def check_if_checked_in_color(checkin, attendee):

    if checkin in attendee.checkins.all():
        return "danger"
    else:
        return "info"


@register.filter(name='ticket_checked')
def ticket_checked(ticket, checkin):
	if checkin.tickets.filter(id=ticket.id):
		return "checked"
	else:
		return None
