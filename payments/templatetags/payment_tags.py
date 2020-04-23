from django import template
from payments.models import Payout, Transaction, Refund, HousePayment
from events.models import EventOrder, EventLiveFee


register = template.Library()


@register.simple_tag
def get_type(instance):

    if instance.transaction:
        if instance.transaction.donation_transaction:
            return "Donation"
        else:
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

    if instance.arqam_house_service_fee:
        if instance.arqam_house_service_fee.live_video:
            event_live_fee = EventLiveFee.objects.get(arqam_house_service_fee=instance.arqam_house_service_fee)
            return f"Virtual Event Fee <ul style='margin-bottom: 0px;'><li>Subscribed Mins: {event_live_fee.subscribed_mins}</li><li> Archived Mins: {event_live_fee.archived_mins}</li></ul><a href='#' style='font-size: 10px;'>More Info</a>"



@register.simple_tag
def get_amount(instance):

    if instance.transaction:
        return instance.transaction.house_amount
    
    if instance.refund:
        return instance.refund.house_amount

    if instance.payout:
        return instance.payout.amount

    if instance.house_payment:
        return instance.house_payment.transaction.house_amount

    if instance.opening_balance:
        return '{0:.2f}'.format(0.00)

    if instance.arqam_house_service_fee:
        if instance.arqam_house_service_fee.free:
            return '{0:.2f}'.format(0.00)
        return instance.arqam_house_service_fee.amount



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

    if instance.arqam_house_service_fee:
        return "#ff8b52"


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

    if instance.arqam_house_service_fee:
        return '<i style="font-size:1.1em;" class="la la-camera"></i>'



