import itertools
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from core.models import TimestampedModel
from django.contrib.auth.models import User
from django.urls import reverse

from phonenumber_field.modelfields import PhoneNumberField
from cities_light.models import City, Region, Country
from arqamhouse.aws.utils import PrivateMediaStorage


# ------------------------------------------- Constants -----------------------------------------
roles = (
			('admin', 'Administrator'),
			('staff', 'Staff'),
		)


house_types = (
			('Individual', 'Individual'),
			('Business', 'Business'),
			('Nonprofit', 'Nonprofit'),
		)


# Create your models here.


# ------------------------------------------- House Model -----------------------------------------
# The House model holds information about the House 

def temp_file_upload_location(instance, filename):
	return "%s/%s/%s" % (instance.name, "identification", filename)

class House(TimestampedModel):
	name = models.CharField(max_length=120, null=True, blank=False)
	email = models.EmailField(blank=True, null=True)
	phone = PhoneNumberField(blank=True, null=True)
	slug = models.SlugField(unique = False, blank=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=True)
	address = models.CharField(max_length=200, null=True, blank=True)
	business_number = models.CharField(max_length=200, null=True, blank=True)
	postal_code = models.CharField(max_length=6, null=True, blank=True)
	house_type = models.CharField(max_length=150, choices=house_types, blank=True, null=True)
	ip_address = models.CharField(max_length=200, null=True, blank=True)
	address_entered = models.BooleanField(default=False)
	verification_pending = models.BooleanField(default=False)
	verified = models.BooleanField(default=False)

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

		if self.region and self.city and self.address and self.postal_code:
			self.address_entered = True

		super().save(*args, **kwargs)


	def get_dashboard_url(self):
		view_name = "houses:dashboard"
		return reverse(view_name)



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


def id_location(instance, filename):
	return "director_ids/%s/%s/%s" % (instance.house.slug, instance.first_name, filename)

class HouseDirector(TimestampedModel):
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
	dob_year = models.PositiveSmallIntegerField(blank=True, null=True)
	dob_month = models.PositiveSmallIntegerField(blank=True, null=True)
	dob_day = models.PositiveSmallIntegerField(blank=True, null=True)
	first_name = models.CharField(max_length=120, null=True, blank=False)
	last_name = models.CharField(max_length=120, null=True, blank=False)
	front_id = models.FileField(upload_to=id_location)
	back_id = models.FileField(upload_to=id_location)


	def __str__(self):
		return "%s" % (self.house.name)










