from django import template
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

from events.models import Attendee, EventQuestion, Answer, OrderAnswer

register = template.Library()


@register.simple_tag
def get_answer_for_attendee(attendee, event_question):
	
    try:
        answer = Answer.objects.get(attendee=attendee, question=event_question)
        return answer.value
    except:
        return "No Data"


@register.simple_tag
def get_answer_for_order(order, event_question):

    try:
        order_answer = OrderAnswer.objects.get(
            order=order, question=event_question)
        return order_answer.value
    except:
        return "No Data"
