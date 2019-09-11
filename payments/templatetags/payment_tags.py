from django import template
from payments.models import Payout, Transaction, Refund, HousePayment
from events.models import EventOrder


register = template.Library()


@register.simple_tag
def get_type(instance):

    if instance.transaction:
        return "Payment"
    
    if instance.refund:
        return "Refund"

    if instance.payout:
        if instance.payout.processed:
            return """Payout - <span style="color:#62c262;">Processed</span> - Sent To '%s'""" % (instance.payout.payout_setting.name)
        else:
            return """Payout - <span style="color:#FF4500;">Pending</span> - Sent to '%s'""" % (instance.payout.payout_setting.name)

    if instance.house_payment:
        return "Funds Added"

    if instance.opening_balance:
        return "Opening Balance"



@register.simple_tag
def get_amount(instance):

    if instance.transaction:
        return instance.transaction.house_amount
    
    if instance.refund:
        return instance.refund.amount

    if instance.payout:
        return instance.payout.amount

    if instance.house_payment:
        return instance.house_payment.transaction.house_amount

    if instance.opening_balance:
        return '{0:.2f}'.format(0.00)



@register.simple_tag
def get_type_color(instance):

    if instance.transaction:
        return "#62c262"
    
    if instance.refund:
        return "#FF4500"

    if instance.payout:
        return "#4599d5"

    if instance.house_payment:
        return "#62c262"

    if instance.opening_balance:
        return "#4599d5"


@register.simple_tag
def get_type_font_weight(instance):

    if instance.transaction:
        return "500"
    
    if instance.refund:
        return "100"

    if instance.payout:
        return "100"

    if instance.house_payment:
        return "500"

    if instance.opening_balance:
        return "500"


@register.simple_tag
def get_type_icon(instance):

    if instance.transaction:
        return '<i style="font-size:1.1em;" class="la la-check-circle"></i>'
    
    if instance.refund:
        return '<i style="font-size:1.1em;" class="la la-refresh"></i>'

    if instance.payout:
        return '<i style="font-size:1.1em;" class="la la-external-link-square"></i>'

    if instance.house_payment:
        return '<i style="font-size:1.1em;" class="la la-bank"></i>'

    if instance.opening_balance:
        return '<i style="font-size:1.1em;" class="la la-flag-checkered"></i>'



