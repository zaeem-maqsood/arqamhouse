from django import template
from payments.models import Payout, Transaction, Refund, HousePayment
from events.models import EventOrder


register = template.Library()


@register.simple_tag
def get_type(instance):

    if isinstance(instance, Payout):
        return "Payout"
    elif isinstance(instance, Refund):
        return "Refund"
    else:
        return "Payment"


@register.simple_tag
def get_type_amount(instance):

    if isinstance(instance, Payout):
        return instance.amount
    elif isinstance(instance, Refund):
        return instance.amount
    else:
        return instance.house_amount


@register.simple_tag
def get_type_color(instance):

    if isinstance(instance, Payout):
        return "#4599d5"
    elif isinstance(instance, Refund):
        return "#e37f7f"
    else:
        return "#62c262"


@register.simple_tag
def get_type_font_weight(instance):

    if isinstance(instance, Payout):
        return "500"
    elif isinstance(instance, Refund):
        return "100"
    else:
        return "500"


@register.simple_tag
def get_type_icon(instance):

    if isinstance(instance, Payout):
        return '<i style="font-size:1.1em;" class="la la-external-link-square"></i>'
    elif isinstance(instance, Refund):
        return '<i style="font-size:1.1em;"  class="la la-refresh"></i>'
    else:
        return '<i style="font-size:1.1em;"  class="la la-check-circle"></i>'


