from .base import *

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
		return self.filter(Q(active=True, deleted=False))
		# return EventQuerySet(self.model, using=self._db)

	def inactive_events(self, **kwargs):
		return self.filter(Q(active=False, deleted=False))

	def deleted_events(self, **kwargs):
		return self.filter(Q(deleted=True))


class Event(TimestampedModel):
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=120, null=True, blank=False)
	url = models.CharField(max_length=120, null=True, blank=True)
	slug = models.SlugField(max_length = 175, unique = False, blank=True)
	start = models.DateTimeField(blank=False, null=True, default=timezone.now)
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

	def get_email_confirmation_view(self):
		view_name = "events:email_confirmation"
		return reverse(view_name, kwargs={"slug": self.slug})

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
		view_name = "events:list_questions"
		return reverse(view_name, kwargs={"slug": self.slug})

	def create_question(self):
		view_name = "questions:create_question"
		return reverse(view_name, kwargs={"one_to_one_type": "events", "one_to_one_id": self.pk})

	def list_orders_view(self):
		view_name = "events:order_list"
		return reverse(view_name, kwargs={"slug": self.slug})

	def list_attendees_view(self):
		view_name = "events:attendee_list"
		return reverse(view_name, kwargs={"slug": self.slug})

	def payout_view(self):
		view_name = "payouts:event_payout"
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




pre_save.connect(event_pre_save_reciever, sender=Event)






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













