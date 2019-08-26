from .base import *

from events.models import Event, AttendeeCommonQuestions
# Register your models here.

admin.site.register(Event)
admin.site.register(AttendeeCommonQuestions)