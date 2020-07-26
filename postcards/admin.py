from django.contrib import admin

from postcards.models import PostCard, PostCardOrder


class PostcardOrderAdmin(admin.ModelAdmin):
    list_display = ('sent_to_recipient', 'post_card', 'name', 'recipient_name',
                    'message_to_recipient', 'recipient_address', 'recipient_postal_code', 'anonymous')
    list_filter = ('post_card',)
    search_fields = ('recipient_name', 'name')


# Register your models here.
admin.site.register(PostCard)
admin.site.register(PostCardOrder, PostcardOrderAdmin)
