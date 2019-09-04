import decimal
from django import template
from django.db.models import Sum
from events.models import Event, Ticket, EventOrder

register = template.Library()

@register.simple_tag
def get_tickets_sold(event):
    amount_sold = Ticket.objects.filter(event=event).aggregate(Sum('amount_sold'))
    print(amount_sold)
    return amount_sold["amount_sold__sum"]


@register.simple_tag
def get_revenue_earned(event):
    revenue = EventOrder.objects.filter(event=event, failed=False, refunded=False).aggregate(Sum('event_cart__total_no_fee'))
    revenue = revenue["event_cart__total_no_fee__sum"]
    return '{0:.2f}'.format(revenue)