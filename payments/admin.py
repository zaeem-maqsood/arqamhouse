from django.contrib import admin

from .models import Transaction, Refund

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Refund)