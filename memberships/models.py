import os
import decimal
from PIL import Image
from datetime import datetime, timedelta
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.utils import timezone

from core.utils import strip_non_ascii

from core.models import TimestampedModel
from houses.models import House


intervals = (
    ('day', 'day'),
    ('week', 'week'),
    ('month', 'month'),
    ('year', 'year'),
)

# Create your models here.

# The MembershipProduct object is the different ''memberships'
# the houses can offer

class MembershipProduct(TimestampedModel):

    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=250, unique=False, blank=True)
    stripe_id = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)

        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not MembershipProduct.objects.filter(house=self.house, slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate

    
    def _update_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.title)
        updated_slug = slugify(value, allow_unicode=True)
        if MembershipProduct.objects.filter(house=self.house, slug=updated_slug).exists():
            pass
        else:
            self.slug = updated_slug


    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        self._update_slug()
        super().save(*args, **kwargs)




# For now we will automatically create this model for each MembershipProduct
# because it allws for simplicity. 
# There will only be 1 MembershipPrice for each MembershipProduct
# A monthly fee the house chooses to set

class MembershipPrice(TimestampedModel):
    membership_product = models.ForeignKey(MembershipProduct, on_delete=models.CASCADE, blank=False, null=False)
    price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=10, null=True, blank=True)
    interval = models.CharField(max_length=150, choices=intervals, blank=True, null=True)
    interval_count = models.PositiveIntegerField(blank=True, null=True, default=1)

    def __str__(self):
        return self.title



