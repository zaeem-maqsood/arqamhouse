

from .base import *
from events.models import Event
from core.models import TimestampedModel


roles = (
    ('user', 'User'),
    ('environment', 'Environment'),
    ('screen', 'Screen'),
)

class EventLive(models.Model):

    event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)
    session_id = models.CharField(max_length=400, blank=True, null=True)
    broadcast_id = models.CharField(max_length=400, blank=True, null=True)
    facing_mode = models.CharField(max_length=150, choices=roles, blank=True, null=True)

    def __str__(self):
        return self.event.title

    def get_live_user_view(self):
        view_name = "events:live_presenter"
        return reverse(view_name, kwargs={"slug": self.event.slug, "mode": 'user'})

    def get_live_environment_view(self):
        view_name = "events:live_presenter"
        return reverse(view_name, kwargs={"slug": self.event.slug, "mode": 'environment'})
    
    def get_live_screen_view(self):
        view_name = "events:live_presenter"
        return reverse(view_name, kwargs={"slug": self.event.slug, "mode": 'screen'})

    def create_facebook_broadcast_view(self):
        view_name = "events:broadcast_facebook"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})

    def create_youtube_broadcast_view(self):
        view_name = "events:broadcast_youtube"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})




class EventLiveBroadcast(TimestampedModel):
    event_live = models.ForeignKey(EventLive, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=120, null=True, blank=True)
    facebook_url = models.CharField(max_length=320, null=True, blank=True)
    youtube_url = models.CharField(max_length=320, null=True, blank=True)
    stream_key = models.CharField(max_length=320, null=True, blank=True)

    def __str__(self):
        return self.event_live.event.title

    def get_update_view(self):
        view_name = "events:broadcast_update"
        return reverse(view_name, kwargs={"slug": self.event_live.event.slug, "pk": self.event_live.id, "broadcast_pk": self.id})



class EventLiveArchive(TimestampedModel):
    event_live = models.ForeignKey(EventLive, on_delete=models.CASCADE, blank=False, null=False)
    archive_id = models.CharField(max_length=400, blank=True, null=True)
    archive_location = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.event_live.event.title

    
    def get_absolute_url(self):
        view_name = "events:achrive_detail"
        return reverse(view_name, kwargs={"slug": self.event_live.event.slug, "pk": self.id})

    


class EventLiveComment(TimestampedModel):

    event_live = models.ForeignKey(EventLive, on_delete=models.CASCADE, blank=False, null=False)
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.CharField(max_length=280, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.event_live.event.title
