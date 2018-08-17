from django.contrib import admin

from .models import EventAnswer, TicketAnswer

# Register your models here.
admin.site.register(EventAnswer)
admin.site.register(TicketAnswer)