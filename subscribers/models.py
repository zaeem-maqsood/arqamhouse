import itertools
import decimal
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

from core.utils import strip_non_ascii
from core.models import TimestampedModel
from houses.models import House

from events.models import EventOrder, Event, Ticket
from donations.models import DonationType

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

    total_events_since_subscribed = models.PositiveIntegerField(blank=True, null=True, default=0)
    total_campaigns_since_subscribed = models.PositiveIntegerField(blank=True, null=True, default=0)

    campaign_views = models.PositiveIntegerField(blank=True, null=True, default=0)
    event_attendance = models.PositiveIntegerField(blank=True, null=True, default=0)
    times_donated = models.PositiveIntegerField(blank=True, null=True, default=0)
    amount_donated = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=2, default=decimal.Decimal('0.00'))


    campaign_view_score = models.PositiveIntegerField(blank=True, null=True, default=100)
    event_score = models.PositiveIntegerField(blank=True, null=True, default=100)
    donation_score = models.PositiveIntegerField(null=True, blank=True, default=100)
    donation_above_average = models.BooleanField(default=False)
    
    events = models.ManyToManyField(Event, blank=True)
    unsubscribed = models.BooleanField(default=False) 
    

    def __str__(self):
        return "%s" % (self.profile.name)

    def get_absolute_url(self):
        view_name = "subscribers:detail"
        return reverse(view_name, kwargs={"slug": self.profile.slug})

    def update_scores(self):
        try:
            self.campaign_view_score = (self.campaign_views / self.total_campaigns_since_subscribed) * 100
        except:
            self.campaign_view_score = 100

        try:
            self.event_score = (self.event_attendance / self.total_events_since_subscribed) * 100
        except:
            self.event_score = 100

        try:
            self.donation_score = (self.times_donated / self.house.donation_score) * 100
        except:
            self.donation_score = 100

        try:
            if self.amount_donated >= self.house.donation_amount_score:
                self.donation_above_average = True
            else:
                self.donation_above_average = False
        except Exception as e: 
            print(e)
            self.donation_above_average = True

    def save(self, *args, **kwargs):
        self.update_scores()
        super().save(*args, **kwargs)








class Audience(TimestampedModel):
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=175, unique=False, blank=True)
    subscribers = models.ManyToManyField(Subscriber, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    donation_type = models.ForeignKey(DonationType, on_delete=models.CASCADE, blank=True, null=True)

    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)

        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Audience.objects.filter(slug=slug_candidate, house=self.house).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate

    
    def _update_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)
        updated_slug = slugify(value, allow_unicode=True)
        if Audience.objects.filter(slug=updated_slug, house=self.house).exists():
            pass
        else:
            self.slug = updated_slug


    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        
        self._update_slug()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


    def get_detail_view(self):
        view_name = "subscribers:audience_detail"
        return reverse(view_name, kwargs={"slug": self.slug})


    def create_campaign_view(self):
        view_name = "subscribers:campaign_create_audience"
        return reverse(view_name, kwargs={"slug": self.slug})









class Campaign(TimestampedModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=False, blank=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    audience = models.ForeignKey(Audience, on_delete=models.CASCADE, blank=True, null=True)
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
    deleted = models.BooleanField(default=False)


    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)

        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Campaign.objects.filter(slug=slug_candidate, house=self.house).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate

    def __str__(self):
        return "%s" % (self.name)

    def update_total_and_seen(self):
        self.total = self.subscribers_sent_to.all().count()
        self.seen = self.subscribers_seen.all().count()
        print("the total is ")

    def update_score(self):
        if self.total > 0:
            score = (self.seen/self.total) * 100
            self.score = score

    def save(self, *args, **kwargs):

        if self.pk:
            self.update_total_and_seen()
            self.update_score()

        if not self.pk:
            self._generate_slug()

        super().save(*args, **kwargs)


    def get_update_view(self):
        view_name = "subscribers:campaign_update"
        return reverse(view_name, kwargs={"slug": self.slug})

    def get_detail_view(self):
        view_name = "subscribers:campaign_detail"
        return reverse(view_name, kwargs={"slug": self.slug})

    def get_detail_content_view(self):
        view_name = "subscribers:campaign_detail_content"
        return reverse(view_name, kwargs={"slug": self.slug})
