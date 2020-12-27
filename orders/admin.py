from django.contrib import admin
from .models import Order, LineOrder, PromoCode

# Register your models here.


class LineOrderAdmin(admin.ModelAdmin):
    list_display = ('sender_address', 'postcard', 'promo_code',
                    'recipient', 'message_to_recipient', 'amount', 'anonymous', 'gift_card')
    search_fields = ('postcard', 'recipient')


admin.site.register(Order)
admin.site.register(LineOrder, LineOrderAdmin)
admin.site.register(PromoCode)

