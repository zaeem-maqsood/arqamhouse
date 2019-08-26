from django import template
from events.models import EventQuestion, EventCart, EventCartItem
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()

from events.models import Ticket, EventQuestion








@register.filter(name='quantity') 
def quantity(number):
    return range(number)


@register.filter(name='ticket_question') 
def ticket_question(cart_item):
    event_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id).order_by("question__order")
    return event_questions












@register.filter(name='order_question') 
def order_question(event):
    order_questions = EventQuestion.objects.filter(event=event, order_question=True).order_by("question__order")
    return order_questions


@register.simple_tag
def get_order_question_initial_value(data, order_question_id):
    try:
        value = data["%s_order_question" % order_question_id]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def get_order_question_initial_value_multiplechoice(data, order_question_id, option):
    try:
        value = data["%s_order_question" % order_question_id]
        if option.title == value:
            return "selected"
        else:
            return ""
    except Exception as e:
        return ""









@register.simple_tag
def get_attendee_name_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_name" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""


@register.simple_tag
def get_attendee_email_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_email" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""


@register.simple_tag
def get_attendee_note_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_note" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def get_attendee_age_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_age" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""


@register.simple_tag
def get_attendee_gender_initial_value(data, quantity, ticket_id, gender):
    try:
        value = data["%s_%s_gender" % (quantity, ticket_id)]
        if gender == value:
            return "selected"
        else:
            return ""
    except Exception as e:
        return ""




@register.simple_tag
def get_attendee_question_initial_value(data, quantity, question_id, ticket_id):
    try:
        value = data["%s_%s_%s" % (quantity, question_id, ticket_id)]
        return value
    except Exception as e:
        return ""


@register.simple_tag
def get_attendee_question_initial_value_multiplechoice(data, quantity, question_id, ticket_id, option):
    try:
        value = data["%s_%s_%s" % (quantity, question_id, ticket_id)]
        if option.title == value:
            return "selected"
        else:
            return ""
    except Exception as e:
        return ""