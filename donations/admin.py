from django.contrib import admin

from .models import Donation, DonationType

# Register your models here.
admin.site.register(DonationType)
admin.site.register(Donation)
