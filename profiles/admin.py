from django.contrib import admin

from .models import Profile

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('email', 'name', 'phone')


admin.site.register(Profile, ProfileAdmin)
