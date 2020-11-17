from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

from postcards.models import PostCard
from recipients.models import Recipient
from profiles.models import Profile

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


class Order(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=False, null=False)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    donation_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    total_donation_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    fulfilled = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=300, null=True, blank=True)
    payment_method_id = models.CharField(max_length=300, null=True, blank=True)

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


class LineOrder(models.Model):


    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    postcard = models.ForeignKey(PostCard, on_delete=models.CASCADE, blank=True, null=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, blank=True, null=True)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, blank=True, null=True)

    # replace with address model --------
    address = models.CharField(max_length=200, null=True, blank=True)
    apt_number = models.CharField(max_length=20, null=True, blank=True)
    street_number = models.CharField(max_length=20, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)
    administrative_area_level_1 = models.CharField(max_length=4, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    # replace with address model --------

    message_to_recipient = models.TextField(blank=True, null=True)

    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    donation_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    anonymous = models.BooleanField(default=False)
    add_gift_card = models.BooleanField(default=False)
    gift_card = models.CharField(max_length=150, choices=gift_cards, blank=True, null=True)
    gift_card_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

    # internal todo list --------------
    sent_to_recipient = models.BooleanField(default=False)
    envelope_printed = models.BooleanField(default=False)
    front_printed = models.BooleanField(default=False)
    name_printed = models.BooleanField(default=False)
    message_printed = models.BooleanField(default=False)
    finished_image = models.ImageField(upload_to=order_image_location, validators=[validate_file_size], null=True, blank=True)
    # internal todo list --------------


    def __str__(self):
        return (self.order.name)
