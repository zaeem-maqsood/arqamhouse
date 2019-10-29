from django.contrib import admin


from .models import House, HouseUser, HouseDirector

# Register your models here.
admin.site.register(House)
admin.site.register(HouseUser)
admin.site.register(HouseDirector)
