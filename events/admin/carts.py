from .base import *
from events.models import EventCart, EventCartItem


class EventCartAdmin(admin.ModelAdmin):
    list_display = ('event', 'processed', 'created_at', 'total_no_fee',
                    'total', 'total_fee', 'arqam_charge', 'stripe_charge', 'pay', 'house_created', 'invalid_discount_code', 'discount_code',)
    list_filter = ('processed', 'pay', 'house_created',
                   'invalid_discount_code', 'created_at')
    search_fields = ('event', 'created_at')


class EventCartItemAdmin(admin.ModelAdmin):
    list_display = ('event_cart', 'ticket', 'quantity',
                    'free_ticket', 'paid_ticket', 'donation_ticket', 'pass_fee', 'discount_code_activated', 'cart_item_total_no_fee', 'cart_item_total', 'cart_item_fee',)
    list_filter = ('free_ticket', 'paid_ticket', 'donation_ticket',
                   'pass_fee', 'discount_code_activated',)
    search_fields = ('event_cart', 'title',)


# Register your models here.
admin.site.register(EventCart, EventCartAdmin)
admin.site.register(EventCartItem, EventCartItemAdmin)
