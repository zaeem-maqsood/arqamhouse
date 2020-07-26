from django.db import models

from django.utils.text import slugify
import itertools
from core.utils import strip_non_ascii
from django.core.exceptions import ValidationError

import decimal
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

def validate_file_size(value):
    print("The file size is %s" % (value.size))
    filesize = value.size
    if filesize > 10242880:
        raise ValidationError(
            "The maximum file size that can be uploaded is 5MB")
    else:
        return value

def image_location(instance, filename):
    return "arqam_house_postcards/%s/%s" % (instance.pk, filename)

class PostCard(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    slug = models.SlugField(unique=False, blank=True)
    description = models.TextField(blank=True, null=True)
    image_1 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_2 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_3 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_4 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_5 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    amount_sold = models.PositiveIntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return (self.name)

    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        
        value = strip_non_ascii(self.name)
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not PostCard.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate


    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        super().save(*args, **kwargs)



    def get_absolute_url(self):
        view_name = "postcards:detail"
        return reverse(view_name, kwargs={"slug": self.slug})





class PostCardOrder(models.Model):

    post_card = models.ForeignKey(PostCard, on_delete=models.CASCADE, blank=False, null=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=False, null=False)
    message_to_recipient = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    anonymous = models.BooleanField(default=False)
    recipient_name = models.CharField(max_length=30, null=True, blank=True)
    recipient_address = models.CharField(max_length=200, null=True, blank=True)
    recipient_postal_code = models.CharField(max_length=10, null=True, blank=True)
    sent_to_recipient = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=150, null=True, blank=True)
    payment_method_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return (self.name)
