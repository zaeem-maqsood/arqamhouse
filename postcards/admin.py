from django.contrib import admin

from postcards.models import PostCard, PostCardOrder

# Register your models here.
admin.site.register(PostCard)
admin.site.register(PostCardOrder)
