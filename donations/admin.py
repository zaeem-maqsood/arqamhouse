from django.contrib import admin

from .models import Donation, DonationType, GiftDonationItem

# Register your models here.
admin.site.register(DonationType)
admin.site.register(Donation)
admin.site.register(GiftDonationItem)
