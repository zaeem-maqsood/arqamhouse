import decimal
from django import template
from django.db.models import Sum
from events.models import Event, Ticket, EventOrder

register = template.Library()

@register.simple_tag
def get_tickets_sold(event):
    amount_sold = Ticket.objects.filter(event=event).aggregate(Sum('amount_sold'))
    print(amount_sold)
    amount_sold = amount_sold["amount_sold__sum"]
    if amount_sold:
        return amount_sold
    else:
        return "0"


@register.simple_tag
def get_revenue_earned(event):
    revenue = EventOrder.objects.filter(event=event, failed=False, refunded=False).aggregate(Sum('transaction__house_amount'))
    revenue = revenue["transaction__house_amount__sum"]
    if revenue:
        return '{0:.2f}'.format(revenue)
    else:
        return '{0:.2f}'.format(0.00)
