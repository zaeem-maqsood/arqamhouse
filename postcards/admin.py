from django.contrib import admin

from postcards.models import PostCard, PostCardOrder, PostCardBusinessOrder, PromoCode, NonProfit


class PostcardOrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'sent_to_recipient', 'post_card', 'recipient_name',
                    'message_to_recipient', 'recipient_address', 'recipient_postal_code', 'anonymous', 'postal_code')
    list_filter = ('post_card',)
    search_fields = ('recipient_name', 'name')


# Register your models here.
admin.site.register(NonProfit)
admin.site.register(PromoCode)
admin.site.register(PostCard)
admin.site.register(PostCardOrder, PostcardOrderAdmin)
admin.site.register(PostCardBusinessOrder)
