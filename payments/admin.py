from django.contrib import admin

from .models import Transaction, Refund, Payout, HousePayment

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Refund)
admin.site.register(Payout)
admin.site.register(HousePayment)