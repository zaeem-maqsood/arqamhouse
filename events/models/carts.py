from .base import *
from .events import Event
from .tickets import Ticket


# Create your models here.
class EventCart(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	processed = models.BooleanField(default=False)
	total_no_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	total = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	total_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	arqam_charge = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	stripe_charge = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	pay = models.BooleanField(default=True)
	house_created = models.BooleanField(default=False)

	def __str__(self):
		return self.event.title

	def update_tickets_available(self):
		event_cart_items = EventCartItem.objects.filter(event_cart=self)
		for event_cart_item in event_cart_items:
			event_cart_item.ticket.amount_sold = (event_cart_item.quantity + event_cart_item.ticket.amount_sold)
			event_cart_item.ticket.save()

	def update_total(self):
		
		# get all items in cart
		event_cart_items = EventCartItem.objects.filter(event_cart=self)

		# Show the total without fees
		total_no_fee = decimal.Decimal(0.00)

		# Show the total fees the customer has to pay
		total_fee = decimal.Decimal(0.00)

		# Show the total for the order (tickets + fees)
		total = decimal.Decimal(0.00)
		
		# Amount Stripe is going to charge us for this transaction
		stripe_charge = decimal.Decimal(0.00)

		# Arqam Profit from this transaction
		arqam_charge = decimal.Decimal(0.00)
		
		stripe_fee = decimal.Decimal(settings.STRIPE_FEE/100)
		stripe_base_fee = decimal.Decimal(settings.STRIPE_BASE_FEE)

		# calculate totals
		for item in event_cart_items:

			total_no_fee += item.cart_item_total_no_fee
			total += item.cart_item_total

			# Calculate total fee
			total_fee += item.cart_item_fee


		# Calculate Stripe charge to us
		if total == 0.00:
			stripe_charge = 0.00
			arqam_charge = 0.00

		else:
			# Calculate Stripe Charge
			stripe_charge = (total * stripe_fee) + stripe_base_fee
			# Calculate Arqam charge
			arqam_charge = total - total_no_fee - stripe_charge

		self.total_fee = total_fee
		self.arqam_charge = arqam_charge
		self.stripe_charge = stripe_charge
		self.total = total
		self.total_no_fee = total_no_fee
		self.save()




class EventCartItem(models.Model):

	event_cart = models.ForeignKey(EventCart, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	quantity = models.PositiveIntegerField(blank=True, null=False)
	donation_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	free_ticket = models.BooleanField(default=False)
	paid_ticket = models.BooleanField(default=False)
	donation_ticket = models.BooleanField(default=False)
	pass_fee = models.BooleanField(default=False)
	ticket_price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	cart_item_total_no_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	cart_item_total = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	cart_item_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

	

	def __str__(self):
		return self.ticket.title


def event_cart_item_pre_save_reciever(sender, instance, *args, **kwargs):

	# Scenario: Ticket is free. If ticket is free set the 'ticket_price' to 0.00
	# and the 'cart_item_total' to 0.00 since any multiplication of 0 is 0
	# also set the 'free_ticket' boolean indicator on
	if instance.ticket.free:
		instance.ticket_price = 0.00
		instance.cart_item_total = 0.00
		instance.cart_item_total_no_fee = 0.00
		instance.cart_item_fee = 0.00
		instance.free_ticket = True
	
	# Scenario: Ticket is a paid ticket. If the ticket is a paid ticket set the 
	# 'ticket_price' to the buyer price created in the ticket model
	# Get the quantity from the model
	# set the 'cart_item_total' by multiplying the 'ticket_price' by the quantity
	# set the 'paid_ticket' boolean indicator on 
	elif instance.ticket.paid:
		instance.paid_ticket = True
		instance.ticket_price = instance.ticket.buyer_price
		quantity = instance.quantity
		if instance.ticket.pass_fee:
			instance.cart_item_total_no_fee = (instance.ticket.price * quantity)
		else:
			instance.cart_item_total_no_fee = ((instance.ticket.price - instance.ticket.fee) * quantity)
		instance.cart_item_total = (instance.ticket.buyer_price * quantity)
		instance.cart_item_fee = (instance.ticket.fee * quantity)

		# Check if the fee is passed on, if so set the 'pass_fee' boolean indicator
		if instance.ticket.pass_fee:
			instance.pass_fee = True

	# Scenario Ticket is a donation ticket. If the ticket is a 'donation_ticket' set
	# the 'ticket_price' to the 'donation_amount' 
	# get the quantity
	# multiply values for 'cart_item_total'
	# For donation tickets im assuming we should pass the fee on but this might need to change
	# later on down the road.
	elif instance.ticket.donation:
		instance.donation_ticket = True
		instance.ticket_price = instance.donation_amount
		quantity = instance.quantity
		instance.cart_item_total_no_fee = (instance.donation_amount * quantity)
		instance.cart_item_total = (instance.donation_amount * quantity)
		instance.pass_fee = True



def event_cart_item_post_save_reciever(sender, instance, *args, **kwargs):
	instance.event_cart.update_total()

pre_save.connect(event_cart_item_pre_save_reciever, sender=EventCartItem)
post_save.connect(event_cart_item_post_save_reciever, sender=EventCartItem)



