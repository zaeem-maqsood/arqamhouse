from django.contrib import admin


from .models import Organization, OrganizationUser

# Register your models here.
admin.site.register(Organization)
admin.site.register(OrganizationUser)