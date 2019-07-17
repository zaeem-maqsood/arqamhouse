from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.urls import reverse

from cities_light.models import City, Region, Country
from django.contrib.auth.models import User
from core.models import TimestampedModel
from houses.models import House


class ProfileManager(BaseUserManager):
	
	def create_user(self, email, password, **extra_fields):
		"""
		Create and save a User with the given email and password.
		"""
		if not email:
			raise ValueError(_('The Email must be set'))
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		"""
		Create and save a SuperUser with the given email and password.
		"""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))
		return self.create_user(email, password, **extra_fields)



# Create your models here.
class Profile(AbstractUser):
	
	username = None
	email = models.EmailField(_('email address'), unique=True)
	name = models.CharField(max_length=120, null=True, blank=False)
	slug = models.SlugField(unique = False, blank=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=True)
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=True)
	objects = ProfileManager()
	
	USERNAME_FIELD = 'email'
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def __str__(self):
		return str(self.email)

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












