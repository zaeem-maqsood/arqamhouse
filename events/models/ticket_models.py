import decimal
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save

from events.models import Event


# Ticket Model ---------------------------------------------------
class Ticket(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=100, null=True, blank=True)
	slug = models.SlugField(max_length = 175, unique = False, blank=True)
	price = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2)
	sale_price = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2)
	buyer_price = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2)
	sale_start = models.DateTimeField(blank=True, null=True)
	sale_end = models.DateTimeField(blank=True, null=True)
	min_amount = models.PositiveSmallIntegerField(blank=True, null=False, default=0)
	max_amount = models.PositiveSmallIntegerField(blank=True, null=False, default=10)
	description = models.TextField(blank=True, null=True)
	paid = models.BooleanField(default=False)
	pass_fee = models.BooleanField(default=True)
	free = models.BooleanField(default=False)
	donation = models.BooleanField(default=False)
	sold_out = models.BooleanField(default=False)
	amount_available = models.PositiveSmallIntegerField(blank=True, null=False, default=1000)
	amount_sold = models.PositiveSmallIntegerField(blank=True, null=False, default=0)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def get_ticket_questions(self):
		return self.ticketquestion_set.filter(ticket=self, deleted=False, approved=True).order_by('order')

	def update_ticket_view(self):
		view_name = "events:update_ticket"
		return reverse(view_name, kwargs={"slug": self.event.slug, "ticket_slug": self.slug})

	def create_ticket_simple_question(self):
		view_name = "events:questions:ticket_create_simple"
		return reverse(view_name, kwargs={"slug": self.event.slug, "ticket_slug": self.slug, "type":"simple"})

	def create_ticket_paragraph_question(self):
		view_name = "events:questions:ticket_create_paragraph"
		return reverse(view_name, kwargs={"slug": self.event.slug, "ticket_slug": self.slug, "type":"paragraph"})

	def create_ticket_multiple_choice_question(self):
		view_name = "events:questions:ticket_create_multiple_choice"
		return reverse(view_name, kwargs={"slug": self.event.slug, "ticket_slug": self.slug, "type":"multiple choice"})

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


def create_slug(instance, new_slug=None):

	slug = slugify(instance.title)
		
	if new_slug is not None:
		slug = new_slug
	qs = Ticket.objects.filter(slug=slug, event=instance.event)
	exists = qs.count() > 1

	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)

	return slug


def ticket_pre_save_reciever(sender, instance, *args, **kwargs):

	instance.slug = create_slug(instance)

	# Check if the ticket is a paid ticket type
	if instance.paid:

		# Check if the user entered a sale price, if so use that as the 'price to calculate'
		if instance.sale_price:
			sale_price = instance.sale_price
			price_to_calculate = decimal.Decimal(sale_price)

		# If the user did not enter a sale price continue with the price for calculation
		elif instance.price:
			price = instance.price
			price_to_calculate = decimal.Decimal(price)

		# If there is no price set the price to 0.00
		else:
			price_to_calculate = 0.00
		
		# Get the Arqam platform fee from settings
		platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)
		# Get the Arqam platform base fee from settings 
		platform_base_fee = decimal.Decimal(settings.PLATFORM_BASE_FEE)


		# Check to see if the user has passed on the fee to the customer, if so add the fee to the ticket price
		# We also have to add the stripe fee, but that will be done in the carts models
		if instance.pass_fee:
			instance.buyer_price = (price_to_calculate + decimal.Decimal((price_to_calculate * platform_fee)) + platform_base_fee)
		else:
			instance.buyer_price = (price_to_calculate)
	else:
		instance.buyer_price = 0.00

pre_save.connect(ticket_pre_save_reciever, sender=Ticket)



