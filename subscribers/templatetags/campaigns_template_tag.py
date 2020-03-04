from events.models import Event, Ticket
from django import template


register = template.Library()


@register.simple_tag
def check_if_ticket_is_checked(ticket, filtered_tickets):
    if filtered_tickets:
        if ticket in filtered_tickets:
            return "checked"
