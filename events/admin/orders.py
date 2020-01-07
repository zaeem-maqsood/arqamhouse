from .base import *
from events.models import EventOrder


class EventOrderAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'created_at', 'number',
                    'public_id', 'house_created',)
    list_filter = ('name', 'number', 'public_id',
                   'house_created', 'created_at')
    search_fields = ('created_at', 'public_id')


admin.site.register(EventOrder, EventOrderAdmin)
