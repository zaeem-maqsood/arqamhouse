from django.contrib import admin

from events.models import Ticket


class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'price',
                    'buyer_price', 'fee', 'express', 'paid', 'pass_fee', 'free', 'donation', 'sold_out', 'deleted')
    list_filter = ('paid', 'pass_fee', 'free',
                   'donation', 'sold_out', 'deleted')
    search_fields = ('event', 'title',)


# Register your models here.
admin.site.register(Ticket, TicketAdmin)
