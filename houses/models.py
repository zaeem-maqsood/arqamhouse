from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from core.models import TimestampedModel
from django.contrib.auth.models import User
from django.urls import reverse

from cities_light.models import City, Region, Country


# ------------------------------------------- Constants -----------------------------------------
roles = (
			('admin', 'Administrator'),
			('staff', 'Staff'),
		)


entity_types = (
			('individual', 'Individual'),
			('company', 'Company'),
		)


# Create your models here.


# ------------------------------------------- House Model -----------------------------------------
# The House model holds information about the House 

def temp_file_upload_location(instance, filename):
	return "%s/%s/%s" % (instance.name, "identification", filename)

class House(TimestampedModel):
	name = models.CharField(max_length=120, null=True, blank=False)
	slug = models.SlugField(unique = False, blank=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=True)


	entity = models.CharField(max_length=150, choices=entity_types, default = 'individual', null=True, blank=True)
	connect_account_created = models.BooleanField(default=False)
	connected_stripe_account_id = models.CharField(max_length=200, null=True, blank=False)
	front_side = models.ImageField(upload_to=temp_file_upload_location, blank=True, null=True)
	back_side = models.ImageField(upload_to=temp_file_upload_location, blank=True, null=True)
	legal_document = models.ImageField(upload_to=temp_file_upload_location, blank=True, null=True)
	stripe_legal_document_id = models.CharField(max_length=200, null=True, blank=True)

	def __str__(self):
		return str(self.name)

	def get_dashboard_url(self):
		view_name = "houses:dashboard"
		return reverse(view_name, kwargs={"slug": self.slug})

	def get_absolute_url(self):
		view_name = "houses:detail"
		return reverse(view_name, kwargs={"slug": self.slug})


def create_slug(instance, new_slug=None):

	slug = slugify(instance.name)
		
	if new_slug is not None:
		slug = new_slug
	qs = House.objects.filter(slug=slug)
	exists = qs.count() > 1

	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)

	return slug


def house_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_slug(instance)

pre_save.connect(house_pre_save_reciever, sender=House)



# ------------------------------------------- House User Model -----------------------------------------
# The House user model links user accounts with houses. It also assigns roles those users have in  
# the houses that they are associated with. 

class HouseUser(TimestampedModel):
	profile = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
	role = models.CharField(max_length=150, choices=roles, default = 'admin')

	def __str__(self):
		return "%s - %s - %s" % (self.profile, self.house, self.role)














