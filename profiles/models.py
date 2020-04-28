from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.urls import reverse
import itertools

from phonenumber_field.modelfields import PhoneNumberField
from core.utils import strip_non_ascii
from stdimage import StdImageField
from cities_light.models import City, Region, Country
from django.contrib.auth.models import User
from core.models import TimestampedModel
from houses.models import House


def validate_file_size(value):
    print("The file size is %s" % (value.size))
    filesize = value.size
    if filesize > 5242880:
        raise ValidationError(
            "The maximum file size that can be uploaded is 5MB")
    else:
        return value


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


def image_location(instance, filename):
    return "profile_pictures/%s/%s" % (instance.email, filename)


# Create your models here.
class Profile(AbstractUser):
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = PhoneNumberField(blank=True, null=True)
    temp_password = models.CharField(max_length=120, null=True, blank=True)
    name = models.CharField(max_length=120, null=True, blank=False)
    picture = StdImageField(upload_to=image_location, validators=[validate_file_size], variations={'thumbnail': {'width': 150, 'height': 150}}, null=True, blank=True)
    slug = models.SlugField(unique = False, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=True)
    subscribed_houses = models.ManyToManyField(House, blank=True, related_name="subscribed_houses")
    stripe_customer_id = models.CharField(max_length=200, null=True, blank=True)
    verified = models.BooleanField(default=False)
    objects = ProfileManager()
    
    USERNAME_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)

    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Profile.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate


    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()

        super().save(*args, **kwargs)

    def get_update_url(self):
        view_name = "profiles:update"
        return reverse(view_name, kwargs={"slug": self.slug})

    def get_absolute_url(self):
        view_name = "profiles:detail"
        return reverse(view_name, kwargs={"slug": self.slug})



def profile_pre_save_reciever(sender, instance, *args, **kwargs):

    # Assign country as Canada
    try:
        canada = Country.objects.get(name="Canada")
        instance.country = canada
    except:
        pass

pre_save.connect(profile_pre_save_reciever, sender=Profile)












