import itertools
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

	def _generate_slug(self):
		max_length = self._meta.get_field('slug').max_length
		# if self.url:
		# 	value = self.url
		# else:
		value = self.name
		slug_candidate = slug_original = slugify(value, allow_unicode=True)
		for i in itertools.count(1):
			if not House.objects.filter(slug=slug_candidate).exists():
				break
			slug_candidate = '{}-{}'.format(slug_original, i)

		self.slug = slug_candidate

	def save(self, *args, **kwargs):
		if not self.pk:
			self._generate_slug()
		super().save(*args, **kwargs)


	def get_dashboard_url(self):
		view_name = "houses:dashboard"
		return reverse(view_name)

	def get_absolute_url(self):
		view_name = "houses:detail"
		return reverse(view_name, kwargs={"slug": self.slug})


def house_pre_save_reciever(sender, instance, *args, **kwargs):
	# Assign country as Canada
	try:
		canada = Country.objects.get(name="Canada")
		instance.country = canada
	except:
		pass

pre_save.connect(house_pre_save_reciever, sender=House)



# ------------------------------------------- House User Model -----------------------------------------
# The House user model links user accounts with houses. It also assigns roles those users have in  
# the houses that they are associated with. 

class HouseUser(TimestampedModel):
	profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False)
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
	role = models.CharField(max_length=150, choices=roles, default = 'admin')

	def __str__(self):
		return "%s - %s - %s" % (self.profile, self.house, self.role)














