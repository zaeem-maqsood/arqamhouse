from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.urls import reverse

from django.contrib.auth.models import User
from core.models import TimestampedModel
from cities.models import (Country, Region, City, District, PostalCode)



timezones = (
        ('Canada/Atlantic', 'Canada Atlantic (-4:00 UTC)'),
        ('Canada/Central', 'Canada Central (-6:00 UTC)'),
        ('Canada/Eastern', 'Canada Eastern (-5:00 UTC)'),
        ('Canada/East-Saskatchewan', 'Canada East-Saskatchewan (-6:00 UTC)'),
        ('Canada/Mountain', 'Canada Mountain (-7:00 UTC)'),
        ('Canada/Newfoundland', 'Canada Newfoundland (-3:30 UTC)'),
        ('Canada/Pacific', 'Canada Pacific (-8:00 UTC)'),
        ('Canada/Saskatchewan', 'Canada Saskatchewan (-6:00 UTC)'),
        ('Canada/Yukon', 'Canada Yukon (-8:00 UTC)'),
)



# Create your models here.
class Profile(TimestampedModel):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	name = models.CharField(max_length=120, null=True, blank=False)
	slug = models.SlugField(unique = False, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)
	timezone = models.CharField(max_length=150, choices=timezones, default = 'Canada/Eastern')
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False, null=True)
	country = models.CharField(max_length=150, default='Canada', blank=False, null=True)


	def __str__(self):
		return str(self.name)

	def get_update_url(self):
		view_name = "profiles:update"
		return reverse(view_name, kwargs={"slug": self.slug})

	def get_absolute_url(self):
		view_name = "profiles:detail"
		return reverse(view_name, kwargs={"slug": self.slug})


def create_slug(instance, new_slug=None):

	slug = slugify(instance.name)
		
	if new_slug is not None:
		slug = new_slug
	qs = Profile.objects.filter(slug=slug)
	exists = qs.count() > 1

	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)

	return slug


def profile_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_slug(instance)

pre_save.connect(profile_pre_save_reciever, sender=Profile)














