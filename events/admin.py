from django.contrib import admin

from .models import Event, EventGeneralQuestions, AttendeeGeneralQuestions
# Register your models here.

admin.site.register(Event)
admin.site.register(EventGeneralQuestions)
admin.site.register(AttendeeGeneralQuestions)