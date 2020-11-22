from django.db import models
from django.utils import timezone
from django.urls import reverse

from profiles.models import Profile

# Create your models here.
class Recipient(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    apt_number = models.CharField(max_length=20, null=True, blank=True)
    street_number = models.CharField(max_length=20, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)
    administrative_area_level_1 = models.CharField(max_length=4, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    counter = models.PositiveIntegerField(blank=True, null=True, default=0)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return (self.name)

    def get_update_url(self):
        view_name = "profiles:recipients:update_recipient"
        return reverse(view_name, kwargs={"id": self.id})
