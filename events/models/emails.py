from .base import *
from events.models import Event


class EventEmailConfirmation(models.Model):

    event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.event.title

