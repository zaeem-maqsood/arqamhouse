import decimal
import itertools
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save

from events.models import Event


# We charge customers a base fee of 30 cents and a percentage of 4% of the ticket price
# PER TICKET. 

refund_policies = (
			('standard', 'Standard'),
			('7-days', '7-days'),
			('30-days', '30-days'),
			('no refunds', 'No Refunds')
		)


# Ticket Model ---------------------------------------------------
class Ticket(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=100, null=True, blank=True)
	slug = models.SlugField(max_length = 175, unique = False, blank=True)

	# Price the user sets 
	price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

	# Price that is determined based on if the user chose to pass the fee or absorb the fee
	buyer_price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

	# Fee
	fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

	express = models.BooleanField(default=False)

	min_amount = models.PositiveSmallIntegerField(blank=True, null=False, default=0)
	max_amount = models.PositiveSmallIntegerField(blank=True, null=False, default=10)
	description = models.TextField(blank=True, null=True)
	paid = models.BooleanField(default=False)
	pass_fee = models.BooleanField(default=True)
	free = models.BooleanField(default=False)
	donation = models.BooleanField(default=False)
	sold_out = models.BooleanField(default=False)
	amount_available = models.PositiveSmallIntegerField(blank=True, null=True, default=500)
	amount_sold = models.PositiveSmallIntegerField(blank=True, null=False, default=0)
	deleted = models.BooleanField(default=False)
	refund_policy = models.CharField(max_length=150, choices=refund_policies, default='standard')

	def __str__(self):
		return self.title

	def _generate_slug(self):
		max_length = self._meta.get_field('slug').max_length
		value = self.title
		slug_candidate = slug_original = slugify(value, allow_unicode=True)
		for i in itertools.count(1):
			if not Ticket.objects.filter(event=self.event, slug=slug_candidate).exists():
				break
			slug_candidate = '{}-{}'.format(slug_original, i)

		self.slug = slug_candidate

	def save(self, *args, **kwargs):
		if not self.pk:
			self._generate_slug()

		super().save(*args, **kwargs)

	def update_ticket_view(self):
		view_name = "events:update_ticket"
		return reverse(view_name, kwargs={"slug": self.event.slug, "ticket_slug": self.slug})

	def percentage_color(self):
		ratio = self.amount_sold / self.amount_available
		if ratio <= 0.5:
			return "bg-success"
		elif ratio > 0.50 and ratio <= 0.70:
			return ""
		elif ratio > 0.70 and ratio <= 0.90:
			return "bg-danger"
		else:
			return "bg-danger"

	def percentage_sold(self):
		ratio = self.amount_sold / self.amount_available
		return "{0:.0f}%".format(ratio * 100)


def ticket_pre_save_reciever(sender, instance, *args, **kwargs):

	# Set the min amount, max amount, and amount available 
	if not instance.min_amount:
		instance.min_amount = 0
	if not instance.max_amount:
		instance.max_amount = 10
	if not instance.amount_available:
		instance.amount_available = 500

	# Set the ticket to sold out 
	if instance.amount_sold == instance.amount_available:
		instance.sold_out = True

	# Check if the ticket is a paid ticket type
	if instance.paid:

		if instance.price:
			price = instance.price
			price_to_calculate = decimal.Decimal(price)

		# If there is no price set the price to 0.00
		else:
			price_to_calculate = 0.00
		
		# Get the Arqam platform fee from settings
		platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)
		# Get the Arqam platform base fee from settings 
		platform_base_fee = decimal.Decimal(settings.PLATFORM_BASE_FEE)

		fee = instance.fee = decimal.Decimal((price_to_calculate * platform_fee)) + platform_base_fee

		# Check to see if the user has passed on the fee to the customer, if so add the fee to the ticket price
		# We also have to add the stripe fee, but that will be done in the carts models
		if instance.pass_fee:
			instance.buyer_price = (price_to_calculate + fee)
		else:
			instance.buyer_price = (price_to_calculate)

	else:
		instance.buyer_price = 0.00

pre_save.connect(ticket_pre_save_reciever, sender=Ticket)



