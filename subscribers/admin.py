from django.contrib import admin

from .models import Subscriber, Campaign


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('profile', 'house', 'created_at')
    list_filter = ('profile', 'house')
    search_fields = ('profile', 'house')


# Register your models here.
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Campaign)
