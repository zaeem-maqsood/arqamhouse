from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import TimestampedModel
from houses.models import House

from events.models import EventOrder, Event

# Create your models here.

engagement_types = (
    ('Often', 'often'),
    ('Sometimes', 'Sometimes'),
    ('Rarely', 'Rarely'),
)

class Subscriber(TimestampedModel):
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    engagement = models.CharField(max_length=150, choices=engagement_types, blank=True, null=True)
    engagement_total = models.PositiveIntegerField(blank=True, null=True, default=0)
    engagement_score = models.PositiveIntegerField(blank=True, null=True, default=0)
    attendance_score = models.PositiveIntegerField(blank=True, null=True, default=0)
    attendance_total = models.PositiveIntegerField(blank=True, null=True, default=0)
    events_total = models.PositiveIntegerField(blank=True, null=True, default=0)
    unsubscribed = models.BooleanField(default=False) 
    

    def __str__(self):
        return "%s" % (self.profile.name)

    def get_absolute_url(self):
        view_name = "subscribers:detail"
        return reverse(view_name, kwargs={"slug": self.profile.slug})

    def update_attendance_score(self):
        if self.events_total > 0:
            self.attendance_score = (self.attendance_total / self.events_total) * 100


    def save(self, *args, **kwargs):
        self.update_attendance_score()
        super().save(*args, **kwargs)



class Campaign(TimestampedModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    subscribers_sent_to = models.ManyToManyField(Subscriber, related_name="subscribers_sent_to", blank=True)
    subscribers_seen = models.ManyToManyField(Subscriber, related_name="subscribers_seen", blank=True)
    # Total number of people the campaign was sent to
    total = models.PositiveIntegerField(blank=True, null=True, default=0)
    # Total number of people who have seen the campaign
    seen = models.PositiveIntegerField(blank=True, null=True, default=0)
    # A score out of 100 for the campaign
    score = models.PositiveIntegerField(blank=True, null=True, default=0)
    content = models.TextField(blank=True, null=True)
    plain_content = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    draft = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.name)


    def get_update_view(self):
        view_name = "subscribers:campaign_update"
        return reverse(view_name, kwargs={"pk": self.id})

