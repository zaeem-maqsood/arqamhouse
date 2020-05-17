import decimal
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.db.models import Sum, Avg

from core.models import TimestampedModel
from payments.models import Transaction
from houses.models import House


# Create your models here.
class DonationType(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=150, null=True, blank=True)
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
    address = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    issue_receipt = models.BooleanField(default=False)
    receipt_number = models.PositiveIntegerField(null=True, blank=True, default=0)
    public_id = models.CharField(max_length=150, null=True, blank=True)
    pass_fee = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)


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


    def update_donation_score(self):

        from subscribers.models import Subscriber
        from subscribers.tasks import update_all_subscribers_who_have_donated

        # First get the subscriber and update their data
        subscriber = Subscriber.objects.get(profile__email=self.email, house=self.donation_type.house)

        subscriber_amount_donated = subscriber.amount_donated
        if subscriber_amount_donated is None:
            subscriber_amount_donated = decimal.Decimal('0.00')
        subscriber_amount_donated += self.transaction.amount
        subscriber.amount_donated = subscriber_amount_donated
        subscriber.save()

        task = update_all_subscribers_who_have_donated.delay(self.donation_type.house.id)



    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_public_id()
            if self.donation_type.house.issue_tax_deductible_receipts:
                self.set_receipt_number()

        self.update_donation_score()

        super().save(*args, **kwargs)


    def get_donation_view(self):
        view_name = "donations:detail"
        return reverse(view_name, kwargs={"public_id": self.public_id})


    
