from .base import *
from events.models import EventLive, EventLiveComment, EventLiveArchive, EventLiveBroadcast, EventLiveFee

admin.site.register(EventLive)
admin.site.register(EventLiveComment)
admin.site.register(EventLiveArchive)
admin.site.register(EventLiveBroadcast)
admin.site.register(EventLiveFee)
