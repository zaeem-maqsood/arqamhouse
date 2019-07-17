from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify
from django.urls import reverse

from core.models import TimestampedModel
from orders.models import Order, EventOrder
from events.models import Ticket
from core.constants import genders
from events.models import Checkin


# Create your models here.

def download_pdf_location(instance, filename):
	return "%s/%s/%s/%s" % (slugify(instance.order.event.House), slugify(instance.order.event), "tickets", filename)


class Attendee(TimestampedModel):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	pdf = models.FileField(upload_to=download_pdf_location, max_length=600, null=True, blank=True)
	name = models.CharField(max_length=150, null=True, blank=True)
	slug = models.SlugField(max_length = 375, unique = False, blank=True)
	email = models.EmailField(max_length=120, null=True, blank=True)
	gender = models.CharField(max_length=20, choices=genders, default='female', null=True, blank=True)

	def __str__(self):
		return self.name


	def get_attendee_view(self):
		view_name = "events:attendees:detail"
		return reverse(view_name, kwargs={"slug": self.order.event.slug, "attendee_slug": self.slug})



	def create_slug(instance):

		slug = slugify(instance.name)
		slug = slug + '-%s' % (instance.id)
		instance.slug = slug
		return instance.slug


# def attendee_pre_save_reciever(sender, instance, *args, **kwargs):
# 	instance.slug = create_slug(instance)

# pre_save.connect(attendee_pre_save_reciever, sender=Attendee)




# Checkin Attendee model ------------
# Check Event app for corresponding Checkin App

class CheckinAttendee(models.Model):
	checkin = models.ForeignKey(Checkin, on_delete=models.CASCADE, blank=False, null=False)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=False, null=False)
	checked = models.BooleanField(default=False)

	def __str__(self):
		return ("%s" % self.attendee.name)






