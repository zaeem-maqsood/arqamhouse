from .base import *
from events.models import EventLive, EventLiveComment, EventLiveArchive, EventLiveBroadcast

admin.site.register(EventLive)
admin.site.register(EventLiveComment)
admin.site.register(EventLiveArchive)
admin.site.register(EventLiveBroadcast)
