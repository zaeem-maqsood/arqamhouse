from django.contrib import admin


from .models import House, HouseUser

# Register your models here.
admin.site.register(House)
admin.site.register(HouseUser)