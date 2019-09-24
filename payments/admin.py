from django.contrib import admin

from .models import Transaction, Refund, Payout, HousePayment, HouseBalance, HouseBalanceLog, PayoutSetting, BankTransfer

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Refund)
admin.site.register(Payout)
admin.site.register(HousePayment)
admin.site.register(HouseBalance)
admin.site.register(HouseBalanceLog)
admin.site.register(PayoutSetting)
admin.site.register(BankTransfer)
