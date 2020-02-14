from .base import *
import itertools
from io import BytesIO, StringIO, TextIOBase
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from bs4 import BeautifulSoup

from core.models import TimestampedModel
from houses.models import House

from django.core.exceptions import ValidationError


# Create your models here.

# Validate Event Image is less than 10MB
def validate_file_size(value):
    filesize = value.size

    if filesize > 5242880:
        raise ValidationError(
            "The maximum file size that can be uploaded is 5MB")
    else:
        return value


def image_location(instance, filename):
    return "event_images/%s/%s" % (instance.house.slug, instance.slug)


def ics_file_location(instance, filename):
    return "event_ics_files/%s/%s/%s" % (instance.house.slug, instance.slug, filename)


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
    title = models.CharField(max_length=50, null=True, blank=False)
    url = models.CharField(max_length=120, null=True, blank=True)
    slug = models.SlugField(max_length = 175, unique = False, blank=True)
    start = models.DateTimeField(blank=True, null=True, default=timezone.now)
    end = models.DateTimeField(blank=True, null=True)
    short_description = models.TextField(null=True, blank=True)
    venue_address = models.CharField(max_length=200, null=True, blank=True)
    venue_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    ticket_sales = models.BooleanField(default=True)
    public = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    send_to_subscribers = models.BooleanField(default=False)
    objects = EventManager()

    def __str__(self):
        return self.title

    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        if self.url:
            value = self.url
        else:
            value = self.title

        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Event.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate

    
    def _update_slug(self):
        max_length = self._meta.get_field('slug').max_length
        if self.url:
            value = self.url
        else:
            value = self.title
        updated_slug = slugify(value, allow_unicode=True)
        if Event.objects.filter(slug=updated_slug).exists():
            pass
        else:
            self.slug = updated_slug


    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        
        self._update_slug()

        super().save(*args, **kwargs)

    

    def get_email_confirmation_view(self):
        view_name = "events:email_confirmation"
        return reverse(view_name, kwargs={"slug": self.slug})

    def get_send_to_subscribers_view(self):
        view_name = "events:send_to_subscribers"
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

    def create_free_ticket(self):
        view_name = "events:create_free_ticket"
        return reverse(view_name, kwargs={"slug": self.slug, "type":"free"})

    def create_paid_ticket(self):
        view_name = "events:create_paid_ticket"
        return reverse(view_name, kwargs={"slug": self.slug, "type":"paid"})

    def create_donation_ticket(self):
        view_name = "events:create_donation_ticket"
        return reverse(view_name, kwargs={"slug": self.slug, "type":"donation"})

    def list_tickets_view(self):
        view_name = "events:list_tickets"
        return reverse(view_name, kwargs={"slug": self.slug})

    def list_questions_view(self):
        view_name = "events:list_questions"
        return reverse(view_name, kwargs={"slug": self.slug})

    def list_discounts_view(self):
        view_name = "events:list_discounts"
        return reverse(view_name, kwargs={"slug": self.slug})

    def create_discount_view(self):
        view_name = "events:create_discount"
        return reverse(view_name, kwargs={"slug": self.slug})

    def list_answers_view(self):
        view_name = "events:answers_list"
        return reverse(view_name, kwargs={"slug": self.slug})

    def list_answers_analytic_view(self):
        view_name = "events:answers_list_analytic"
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

    def checkin_view(self):
        view_name = "events:checkins"
        return reverse(view_name, kwargs={"slug": self.slug})

    def create_checkin_view(self):
        view_name = "events:create_checkin"
        return reverse(view_name, kwargs={"slug": self.slug})


def event_post_save_reciever(sender, instance, *args, **kwargs):

    from events.models import EventEmailConfirmation
    try:
        # Check if email conf exists
        EventEmailConfirmation.objects.get(event=instance)
    except:
        # Create Email Confirmation object
        EventEmailConfirmation.objects.create(event=instance)

post_save.connect(event_post_save_reciever, sender=Event)













