from .base import *
import os
from events.models import Event
from core.models import TimestampedModel
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_file_size(value):
    filesize = value.size
    if filesize > 15728640:
        raise ValidationError(
            "The maximum file size that can be uploaded is 5MB")
    else:
        return value


def event_resource_location(instance, filename):
	return "event_resources/%s/%s/%s" % (instance.event.house.slug, instance.event.slug, filename)


def event_resource_image_location(instance, filename):
    return "event_resources/%s/%s/%s" % (instance.event.house.slug, instance.event.slug, filename)


class EventResource(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=120, null=True, blank=True)
    file = models.FileField(upload_to=event_resource_location, blank=True, null=True, validators=[validate_file_extension, validate_file_size])
    image = models.ImageField(upload_to=event_resource_image_location, validators=[validate_file_size], null=True, blank=True)
    link = models.CharField(max_length=320, null=True, blank=True)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        view_name = "events:resource_detail"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})

    def get_edit_url(self):
        view_name = "events:update_resource"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})
