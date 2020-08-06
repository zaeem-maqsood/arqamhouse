from django import template
from events.models import EventQuestion, EventCart, EventCartItem
from questions.models import MultipleChoice
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()
