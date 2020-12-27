import os
from django.db import models

from django.utils.text import slugify
import itertools
from core.utils import strip_non_ascii
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

import decimal
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from stdimage import StdImageField

# Create your models here.


gift_cards = (
    ('Apple', 'Apple'),
    ('Google', 'Google'),
    ('HomeSense', 'HomeSense'),
    ('Amazon', 'Amazon'),
    ('Indigo', 'Indigo'),
    ('Shoppers', 'Shoppers'),
)

def validate_file_size(value):
    print("The file size is %s" % (value.size))
    filesize = value.size
    if filesize > 10242880:
        raise ValidationError(
            "The maximum file size that can be uploaded is 5MB")
    else:
        return value


def order_image_location(instance, filename):
    return "arqam_house_postcards/orders/%s/%s" % (instance.id, filename)

def image_location(instance, filename):
    return "arqam_house_postcards/%s/%s" % (instance.slug, filename)


def non_profit_logo_location(instance, filename):
    return "non_profit_logos/%s/%s" % (instance.name, filename)



# Non-Profit Organization
class NonProfit(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    slug = models.SlugField(unique=False, blank=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    website = models.URLField(max_length=300, blank=True, null=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    featured = models.BooleanField(default=False)
    logo = models.ImageField(upload_to=non_profit_logo_location, validators=[validate_file_size], null=True, blank=True)

    def __str__(self):
        return (self.name)


    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not NonProfit.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)
        self.slug = slug_candidate

    
    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        view_name = "postcards:non_profit_list"
        return reverse(view_name, kwargs={"slug": self.slug})





class PostCard(models.Model):
    non_profit = models.ForeignKey(NonProfit, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    slug = models.SlugField(unique=False, blank=True)
    description = models.TextField(blank=True, null=True)
    image_1 = StdImageField(upload_to=image_location, validators=[validate_file_size], variations={'thumbnail': {'width': 672, 'height': 480}, 'main': {'width': 1400, 'height': 1000}}, null=True, blank=True)
    image_2 = StdImageField(upload_to=image_location, validators=[validate_file_size], variations={'thumbnail': {'width': 672, 'height': 480}, 'main': {'width': 1400, 'height': 1000}}, null=True, blank=True)
    image_3 = StdImageField(upload_to=image_location, validators=[validate_file_size], variations={'thumbnail': {'width': 672, 'height': 480}, 'main': {'width': 1400, 'height': 1000}}, null=True, blank=True)
    image_4 = StdImageField(upload_to=image_location, validators=[validate_file_size], variations={'thumbnail': {'width': 672, 'height': 480}, 'main': {'width': 1400, 'height': 1000}}, null=True, blank=True)
    image_5 = StdImageField(upload_to=image_location, validators=[validate_file_size], variations={'thumbnail': {'width': 672, 'height': 480}, 'main': {'width': 1400, 'height': 1000}}, null=True, blank=True)
    business_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    amount_sold = models.PositiveIntegerField(null=True, blank=True, default=0)
    featured = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    

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

    @property
    def image_1_path(self):
        filename = os.path.basename(self.image_1.name)
        return f"media/arqam_house_postcards/{self.slug}/{filename}"


    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
        super().save(*args, **kwargs)



    def get_absolute_url(self):
        view_name = "postcards:detail"
        return reverse(view_name, kwargs={"slug": self.slug})

    def order_choose_senders(self):
        view_name = "postcards:order_view_senders"
        return reverse(view_name, kwargs={"slug": self.slug})

    def order_choose_recipients(self):
        view_name = "postcards:order_view_recipients"
        return reverse(view_name, kwargs={"slug": self.slug})

    def get_business_url(self):
        view_name = "postcards:business_step_1"
        return reverse(view_name, kwargs={"slug": self.slug})




class PostCardBusinessOrder(models.Model):

    created_at = models.DateTimeField(default=timezone.now)
    post_card = models.ForeignKey(PostCard, on_delete=models.CASCADE, blank=False, null=True)

    name = models.CharField(max_length=30, null=True, blank=True)
    company_name = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=False, null=False)

    address = models.CharField(max_length=200, null=True, blank=True)
    street_number = models.CharField(max_length=20, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)
    administrative_area_level_1 = models.CharField(max_length=4, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)

    website = models.CharField(max_length=200, null=True, blank=True)
    phone = PhoneNumberField(blank=True, null=True)

    def __str__(self):
        return (self.name)




class PromoCode(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    code = models.CharField(max_length=100, null=True, blank=True, validators=[alphanumeric])
    fixed_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    total_uses = models.PositiveIntegerField(blank=True, null=True, default=1000)
    used = models.PositiveIntegerField(blank=True, null=True, default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return (self.code)


    

# Create an order model



class PostCardOrder(models.Model):

    created_at = models.DateTimeField(default=timezone.now)
    post_card = models.ForeignKey(PostCard, on_delete=models.CASCADE, blank=False, null=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=False, null=False)
    message_to_recipient = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    apt_number = models.CharField(max_length=20, null=True, blank=True)
    street_number = models.CharField(max_length=20, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)
    administrative_area_level_1 = models.CharField(max_length=4, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    donation_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    anonymous = models.BooleanField(default=False)
    add_gift_card = models.BooleanField(default=False)
    gift_card = models.CharField(max_length=150, choices=gift_cards, blank=True, null=True)
    gift_card_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    recipient_name = models.CharField(max_length=30, null=True, blank=True)
    recipient_address = models.CharField(max_length=200, null=True, blank=True)
    recipient_apt_number = models.CharField(max_length=20, null=True, blank=True)
    recipient_street_number = models.CharField(max_length=20, null=True, blank=True)
    recipient_route = models.CharField(max_length=100, null=True, blank=True)
    recipient_locality = models.CharField(max_length=100, null=True, blank=True)
    recipient_administrative_area_level_1 = models.CharField(max_length=4, null=True, blank=True)
    recipient_postal_code = models.CharField(max_length=10, null=True, blank=True)
    sent_to_recipient = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=300, null=True, blank=True)
    payment_method_id = models.CharField(max_length=300, null=True, blank=True)
    envelope_printed = models.BooleanField(default=False)
    front_printed = models.BooleanField(default=False)
    name_printed = models.BooleanField(default=False)
    message_printed = models.BooleanField(default=False)
    finished_image = models.ImageField(upload_to=order_image_location, validators=[validate_file_size], null=True, blank=True)

    def __str__(self):
        return (self.name)


    @property
    def finished_image_path(self):
        filename = os.path.basename(self.finished_image.name)
        return f"media/arqam_house_postcards/orders/{self.pk}/{filename}"



    

