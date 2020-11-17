from django.contrib import admin
from .models import Order, LineOrder, PromoCode

# Register your models here.
admin.site.register(Order)
admin.site.register(LineOrder)
admin.site.register(PromoCode)
