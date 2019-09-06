from django.db import models
from houses.models import House
from django.utils import timezone

# Create your models here.

class Payout(models.Model):

	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
	created_at = models.DateTimeField(default=timezone.now, null=True)
	amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2)


	def __str__(self):
		return (self.house.name)



class Transaction(models.Model):
	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=False)
	payout = models.ForeignKey(Payout, on_delete=models.CASCADE, blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now, null=True)

	amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	house_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	stripe_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	arqam_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

	payment_id = models.CharField(max_length=150, null=True, blank=True)
	failed = models.BooleanField(default=False)
	code_fail_reason = models.CharField(max_length=250, null=True, blank=True)
	failure_code = models.CharField(max_length=150, null=True, blank=True)
	failure_message = models.CharField(max_length=150, null=True, blank=True)
	last_four = models.CharField(max_length=10, null=True, blank=True)
	brand = models.CharField(max_length=100, null=True, blank=True)
	network_status = models.CharField(max_length=150, null=True, blank=True)
	reason = models.CharField(max_length=150, null=True, blank=True)
	risk_level = models.CharField(max_length=150, null=True, blank=True)
	seller_message = models.CharField(max_length=150, null=True, blank=True)
	outcome_type = models.CharField(max_length=150, null=True, blank=True)
	name = models.CharField(max_length=250, null=True, blank=True)
	address_line_1 = models.CharField(max_length=150, null=True, blank=True)
	address_state = models.CharField(max_length=150, null=True, blank=True)
	address_postal_code = models.CharField(max_length=150, null=True, blank=True)
	address_city = models.CharField(max_length=150, null=True, blank=True)
	address_country = models.CharField(max_length=150, null=True, blank=True)


	def __str__(self):
		return (self.house.name)




class Refund(models.Model):

	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
	amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	partial_refund = models.BooleanField(default=False)
	created_at = models.DateTimeField(default=timezone.now, null=True)

	def __str__(self):
		return (self.transaction.house.name)



class HousePayment(models.Model):
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
	created_at = models.DateTimeField(default=timezone.now, null=True)

	def __str__(self):
		return (self.transaction.house.name)

