from .base import *
from events.models import EventCart, EventCartItem

# Register your models here.
admin.site.register(EventCart)
admin.site.register(EventCartItem)