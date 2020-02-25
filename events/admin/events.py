from .base import *

from events.models import Event, AttendeeCommonQuestions, EventRefererDomain
# Register your models here.

admin.site.register(Event)
admin.site.register(AttendeeCommonQuestions)
admin.site.register(EventRefererDomain)
