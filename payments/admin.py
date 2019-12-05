from django.contrib import admin

from .models import Transaction, Refund, Payout, HousePayment, HouseBalance, HouseBalanceLog, PayoutSetting


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('house', 'created_at', 'amount')
    list_filter = ('house',)
    search_fields = ('house__name', 'payment_id')

class HouseBalanceLogAdmin(admin.ModelAdmin):
    list_display = ('house_balance', 'balance', 'created_at')
    list_filter = ('house_balance__house', )
    search_fields = ('house_balance__house',)


class HouseBalanceAdmin(admin.ModelAdmin):
    list_display = ('house', 'balance')
    search_fields = ('house',)


class HousePaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'created_at')


class PayoutSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'house', 'transit', 'institution', 'account')
    list_filter = ('house', )
    search_fields = ('name',)


class PayoutAdmin(admin.ModelAdmin):
    list_display = ('house', 'created_at', 'processed', 'freeze', 'amount', 'payout_setting')
    list_filter = ('house', )
    search_fields = ('house',)


class RefundAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'amount', 'house_amount', 'partial_refund', 'created_at')
    list_filter = ('transaction__house', 'partial_refund', )
    search_fields = ('transaction', 'house',)


# Register your models here.
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Refund, RefundAdmin)
admin.site.register(Payout, PayoutAdmin)
admin.site.register(HousePayment, HousePaymentAdmin)
admin.site.register(HouseBalance, HouseBalanceAdmin)
admin.site.register(HouseBalanceLog, HouseBalanceLogAdmin)
admin.site.register(PayoutSetting, PayoutSettingAdmin)
