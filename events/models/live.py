

from .base import *
from events.models import Event


roles = (
    ('user', 'User'),
    ('environment', 'Environment'),
    ('screen', 'Screen'),
)

class EventLive(models.Model):

    event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)
    session_id = models.CharField(max_length=400, blank=True, null=True)
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
