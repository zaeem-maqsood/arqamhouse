import decimal
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.db.models import Sum, Avg
from django.core.exceptions import ValidationError

from core.models import TimestampedModel
from payments.models import Transaction, Refund
from houses.models import House


# Create your models here.
def validate_file_size(value):
    print("The file size is %s" % (value.size))
    filesize = value.size
    if filesize > 5242880:
        raise ValidationError(
            "The maximum file size that can be uploaded is 5MB")
    else:
        return value

def image_location(instance, filename):
    return "house_gift_donations/%s/%s" % (instance.pk, filename)

class GiftDonationItem(TimestampedModel):

    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image_1 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_2 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_3 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_4 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    image_5 = models.ImageField(upload_to=image_location, validators=[validate_file_size], null=True, blank=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    deleted = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    amount_sold = models.PositiveIntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return (self.name)


    def gift_donation_url(self):
        view_name = "gift_donate"
        return reverse(view_name, kwargs={"pk": self.id, "slug": self.house.slug})




class DonationType(TimestampedModel):

    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    pass_fee = models.BooleanField(default=False)
    issue_receipts = models.BooleanField(default=False)
    general_donation = models.BooleanField(default=False)
    collect_address = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return (self.name)

    def get_update_url(self):
        view_name = "donations:update_type"
        return reverse(view_name, kwargs={"pk": self.id})



class Donation(TimestampedModel):

    donation_type = models.ForeignKey(DonationType, on_delete=models.CASCADE, blank=False, null=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=300, blank=False, null=False)
    message = models.CharField(max_length=100, null=True, blank=True)
    message_to_recipient = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    issue_receipt = models.BooleanField(default=False)
    receipt_number = models.PositiveIntegerField(null=True, blank=True, default=0)
    public_id = models.CharField(max_length=150, null=True, blank=True)
    pass_fee = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    refund_reason = models.TextField(blank=True, null=True)
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, blank=True, null=True)
    gift_donation_item = models.ForeignKey(GiftDonationItem, on_delete=models.CASCADE, blank=True, null=True)
    gift_donation_item_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    recipient_name = models.CharField(max_length=150, null=True, blank=True)
    recipient_email = models.EmailField(max_length=300, blank=True, null=True)
    recipient_address = models.CharField(max_length=200, null=True, blank=True)
    recipient_postal_code = models.CharField(max_length=10, null=True, blank=True)
    send_e_card = models.BooleanField(default=False)


    def __str__(self):
        return (self.name)

    def set_receipt_number(self):
        self.issue_receipt = True
        donations = Donation.objects.filter(donation_type__house=self.donation_type.house)
        donations_exist = donations.exists()
        if donations_exist:
            latest_donation = donations.order_by("-created_at")[0]
            self.number = latest_donation.number + 1
        else:
            self.number = 1

    def generate_public_id(self):
        while True:
            public_id = get_random_string(length=32)
            try:
                Donation.objects.get(public_id=public_id)
            except:
                break
        self.public_id = public_id


    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_public_id()
            if self.donation_type.house.issue_tax_deductible_receipts:
                self.set_receipt_number()

        super().save(*args, **kwargs)


    def get_donation_view(self):
        view_name = "donations:detail"
        return reverse(view_name, kwargs={"public_id": self.public_id})


    


