from django.contrib import admin

from .models import EventCart, EventCartItem

# Register your models here.
admin.site.register(EventCart)
admin.site.register(EventCartItem)