import os
from PIL import Image
from datetime import datetime, timedelta
from django.urls import reverse
from django.db.models import Q
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save

from core.models import TimestampedModel
from houses.models import House

# Create your models here.


def image_location(instance, filename):
	return "event_images/%s/%s" % (instance.house.slug, instance.slug)

class EventQuerySet(models.QuerySet):
	
	def active_events(self):
		return self.filter(active=True)


class EventManager(models.Manager):

	def active_events(self, **kwargs):
		# return self.filter(Q(active=True, deleted=False))
		return EventQuerySet(self.model, using=self._db)

	def inactive_events(self, **kwargs):
		return self.filter(Q(active=False, deleted=False))

	def deleted_events(self, **kwargs):
		return self.filter(Q(deleted=True))


class Event(TimestampedModel):
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=120, null=True, blank=False)
	url = models.CharField(max_length=120, null=True, blank=True)
	slug = models.SlugField(max_length = 175, unique = False, blank=True)
	start = models.DateTimeField(blank=False, null=True)
	end = models.DateTimeField(blank=False, null=True)
	short_description = models.TextField(null=True, blank=True)
	venue_address = models.CharField(max_length=200, null=True, blank=True)
	venue_name = models.CharField(max_length=200, null=True, blank=True)
	short_description = models.TextField(blank=True, null=True)
	image = models.ImageField(upload_to=image_location, null=True, blank=True)
	public = models.BooleanField(default=True)
	active = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)
	objects = EventManager()

	def __str__(self):
		return self.title

	def get_landing_view(self):
		view_name = "events:landing"
		return reverse(view_name, kwargs={"slug": self.slug})

	def get_update_view(self):
		view_name = "events:update"
		return reverse(view_name, kwargs={"slug": self.slug})

	def get_event_dashboard(self):
		view_name = "events:dashboard"
		return reverse(view_name, kwargs={"slug": self.slug})

	def get_event_description(self):
		view_name = "events:description"
		return reverse(view_name, kwargs={"slug": self.slug})

	def create_free_ticket(self):
		view_name = "events:create_free_ticket"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"free"})

	def create_paid_ticket(self):
		view_name = "events:create_paid_ticket"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"paid"})

	def create_donation_ticket(self):
		view_name = "events:create_donation_ticket"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"donation"})

	def choose_tickets_view(self):
		view_name = "events:choose_tickets"
		return reverse(view_name, kwargs={"slug": self.slug})

	def list_tickets_view(self):
		view_name = "events:list_tickets"
		return reverse(view_name, kwargs={"slug": self.slug})

	def list_questions_view(self):
		view_name = "events:questions:list_questions"
		return reverse(view_name, kwargs={"slug": self.slug})

	def create_simple_question(self):
		view_name = "events:questions:create_simple"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"simple"})

	def create_paragraph_question(self):
		view_name = "events:questions:create_paragraph"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"paragraph"})

	def create_multiple_choice_question(self):
		view_name = "events:questions:create_multiple_choice"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"multiple choice"})

	def create_all_ticket_simple_question(self):
		view_name = "events:questions:all_ticket_create_simple"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"simple"})

	def create_all_ticket_paragraph_question(self):
		view_name = "events:questions:all_ticket_create_paragraph"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"paragraph"})

	def create_all_ticket_multiple_choice_question(self):
		view_name = "events:questions:all_ticket_create_multiple_choice"
		return reverse(view_name, kwargs={"slug": self.slug, "type":"multiple choice"})

	def list_orders_view(self):
		view_name = "events:orders:list"
		return reverse(view_name, kwargs={"slug": self.slug})

	def list_attendees_view(self):
		view_name = "events:attendees:list"
		return reverse(view_name, kwargs={"slug": self.slug})

	def payout_view(self):
		view_name = "payouts:event_payout"
		return reverse(view_name, kwargs={"slug": self.slug})


	def create_checkin_view(self):
		view_name = "events:create_checkin"
		return reverse(view_name, kwargs={"slug": self.slug})


def create_slug(instance, new_slug=None):

	if instance.url:
		slug = slugify(instance.url)
	else:
		slug = slugify(instance.title)
		
	if new_slug is not None:
		slug = new_slug
	qs = Event.objects.filter(slug=slug)
	exists = qs.count() > 1

	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)

	return slug



def event_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_slug(instance)

def event_post_save_reciever(sender, instance, *args, **kwargs):
	try:
		event_general_questions = EventGeneralQuestions.objects.get(event=instance)
	except:
		EventGeneralQuestions.objects.create(event=instance)
	try:
		attendee_general_questions = AttendeeGeneralQuestions.objects.get(event=instance)
	except:
		AttendeeGeneralQuestions.objects.create(event=instance)


pre_save.connect(event_pre_save_reciever, sender=Event)
post_save.connect(event_post_save_reciever, sender=Event)



# Frequently Asked General Questions --------------------------------------
class EventGeneralQuestions(models.Model):
	event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)
	
	notes = models.BooleanField(default=False)
	notes_required = models.BooleanField(default=False) 

	def __str__(self):
		return ("%s" % self.event.title)



# Frequently Asked Attendee Questions --------------------------------------
class AttendeeGeneralQuestions(models.Model):
	event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)

	gender = models.BooleanField(default=True)

	email = models.BooleanField(default=False)
	email_required = models.BooleanField(default=False)

	def __str__(self):
		return ("%s" % self.event.title)



# Checkin Model -------------------------
# Check attendee app for corresponding 'CheckinAttendee' model

class Checkin(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=120, null=True, blank=False)
	auto_add_new_attendees = models.BooleanField(default=True)
	password_protected = models.BooleanField(default=True)
	password = models.CharField(max_length=120, null=True, blank=False)

	def __str__(self):
		return ("%s" % self.event.title)













