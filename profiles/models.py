from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.urls import reverse

from cities_light.models import City, Region, Country
from django.contrib.auth.models import User
from core.models import TimestampedModel
from organizations.models import Organization



# Create your models here.
class Profile(TimestampedModel):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	name = models.CharField(max_length=120, null=True, blank=False)
	slug = models.SlugField(unique = False, blank=True)
	email = models.EmailField(max_length=254, null=True, blank=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=True)



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




class SelectedOrganization(TimestampedModel):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return "%s - %s" % (self.user, self.organization)











