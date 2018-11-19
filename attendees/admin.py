from django.contrib import admin

from .models import Attendee
# Register your models here.


class AttendeeAdmin(admin.ModelAdmin):
	list_display = ["order", "ticket", "name", "slug", "email", "gender", "created_at",]
	search_fields = ["order", "ticket", "name", "slug", "email", "gender", "created_at",]
	list_filter = ["gender"]
	class Meta:
		model = Attendee



admin.site.register(Attendee, AttendeeAdmin)