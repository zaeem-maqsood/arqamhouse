from .base import *
from events.models import EventLive, EventLiveComment

admin.site.register(EventLive)
admin.site.register(EventLiveComment)
