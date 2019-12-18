from .base import *
from .events import Event
from .tickets import Ticket
from .discounts import EventDiscount


# Create your models here.
class EventCart(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	created_at = models.DateTimeField(default=timezone.now)
	processed = models.BooleanField(default=False)
	total_no_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	total = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	total_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	arqam_charge = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	stripe_charge = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	pay = models.BooleanField(default=True)
	house_created = models.BooleanField(default=False)
	invalid_discount_code = models.BooleanField(default=False)
	discount_code = models.ForeignKey(EventDiscount, on_delete=models.CASCADE, blank=True, null=True)

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


class ChargeError(models.Model):
	event_cart = models.ForeignKey(EventCart, on_delete=models.CASCADE, blank=False, null=False)
	payment_id = models.CharField(max_length=150, null=True, blank=True)
	failure_code = models.CharField(max_length=150, null=True, blank=True)
	failure_message = models.CharField(max_length=150, null=True, blank=True)
	outcome_type = models.CharField(max_length=150, null=True, blank=True)
	network_status = models.CharField(max_length=150, null=True, blank=True)
	reason = models.CharField(max_length=150, null=True, blank=True)
	name = models.CharField(max_length=250, null=True, blank=True)
	email = models.EmailField(max_length=300, blank=False, null=False)

	def __str__(self):
		return self.event_cart.event.title



class EventCartItem(models.Model):

	event_cart = models.ForeignKey(EventCart, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	quantity = models.PositiveIntegerField(blank=True, null=False)
	donation_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	donation_buyer_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	donation_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	free_ticket = models.BooleanField(default=False)
	paid_ticket = models.BooleanField(default=False)
	donation_ticket = models.BooleanField(default=False)
	pass_fee = models.BooleanField(default=False)
	ticket_price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	ticket_buyer_price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	ticket_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	cart_item_total_no_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	cart_item_total = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	cart_item_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	discount_code_activated = models.BooleanField(default=False)
	discount_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	discount_fixed_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	discount_percentage_amount = models.PositiveSmallIntegerField(blank=True, null=True)

	

	def __str__(self):
		return self.ticket.title


def event_cart_item_pre_save_reciever(sender, instance, *args, **kwargs):

	# Scenario: Ticket is free. If ticket is free set the 'ticket_price' to 0.00
	# and the 'cart_item_total' to 0.00 since any multiplication of 0 is 0
	# also set the 'free_ticket' boolean indicator on
	if instance.ticket.free:
		instance.ticket_price = 0.00
		instance.ticket_buyer_price = 0.00
		instance.ticket_fee = 0.00
		instance.cart_item_total = 0.00
		instance.cart_item_total_no_fee = 0.00
		instance.cart_item_fee = 0.00
		instance.free_ticket = True
	
	# Scenario: Ticket is a paid ticket.
	elif instance.ticket.paid:

		# Set the flag to paid ticket
		instance.paid_ticket = True

		# Check if there is a discount code that can be applied to this cart item
		if instance.event_cart.discount_code and instance.ticket in instance.event_cart.discount_code.tickets.all():

			# Discount code activated flag
			instance.discount_code_activated = True

			# Reduce used amount on discount code
			instance.event_cart.discount_code.used += 1
			instance.event_cart.discount_code.save()

			# find out if the discount code is a fixed amount or a percentage amount
			# take the price of the ticket 'ticket.price' and subtract the discount from it 
			discount_code = instance.event_cart.discount_code
			if discount_code.use_fixed_amount:
				discount_ticket_price = instance.ticket.price - discount_code.fixed_amount
				instance.discount_fixed_amount = discount_code.fixed_amount
			else:
				discount_ticket_price = instance.ticket.price - (instance.ticket.price * decimal.Decimal(discount_code.percentage_amount/100))
				instance.discount_percentage_amount = discount_code.percentage_amount

			# Check to make sure the the new discount price is greater than 1
			if discount_ticket_price >= decimal.Decimal(1.00):

				# Save the new ticket price value
				instance.ticket_price = discount_ticket_price 
				# Save the discount amount
				instance.discount_amount = instance.ticket.buyer_price - discount_ticket_price


				platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)
				platform_base_fee = decimal.Decimal(settings.PLATFORM_BASE_FEE)
				# Find out the new fee based off the discounts applied to the ticket price
				fee = decimal.Decimal((discount_ticket_price * platform_fee)) + platform_base_fee
				instance.ticket_fee = fee

				# Set the quantity
				quantity = instance.quantity

				# Check if the organizer wants to pass the fee or absorb the fee
				# Find out the new discounted ticket buyer price 
				if instance.ticket.pass_fee:
					instance.cart_item_total_no_fee = (discount_ticket_price * quantity)
					discount_ticket_buyer_price = (discount_ticket_price + fee)
				else:
					instance.cart_item_total_no_fee = ((discount_ticket_price - fee) * quantity)
					discount_ticket_buyer_price = (discount_ticket_price)

				# Save the new ticket buyer price
				instance.ticket_buyer_price = discount_ticket_buyer_price
					
				instance.cart_item_total = (discount_ticket_buyer_price * quantity)
				instance.cart_item_fee = (fee * quantity)

			# If the discount is greater than the ticket original price make it free
			else:

				discount_ticket_price = decimal.Decimal(0.00)
				if discount_code.use_fixed_amount:
					instance.discount_fixed_amount = instance.ticket.buyer_price
				else:
					instance.discount_percentage_amount = 100

				# Save the new ticket price value
				instance.ticket_price = discount_ticket_price
				# Save the discount amount
				instance.discount_amount = instance.ticket.buyer_price - discount_ticket_price

				platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)
				platform_base_fee = decimal.Decimal(settings.PLATFORM_BASE_FEE)
				# Find out the new fee based off the discounts applied to the ticket price
				fee = decimal.Decimal(0.00)
				instance.ticket_fee = fee

				# Set the quantity
				quantity = instance.quantity

				# Check if the organizer wants to pass the fee or absorb the fee
				# Find out the new discounted ticket buyer price
				if instance.ticket.pass_fee:
					instance.cart_item_total_no_fee = (discount_ticket_price * quantity)
					discount_ticket_buyer_price = (discount_ticket_price + fee)
				else:
					instance.cart_item_total_no_fee = ((discount_ticket_price - fee) * quantity)
					discount_ticket_buyer_price = (discount_ticket_price)

				# Save the new ticket buyer price
				instance.ticket_buyer_price = discount_ticket_buyer_price

				instance.cart_item_total = (discount_ticket_buyer_price * quantity)
				instance.cart_item_fee = (fee * quantity)


		else:
			instance.ticket_price = instance.ticket.price
			instance.ticket_buyer_price = instance.ticket.buyer_price
			instance.ticket_fee = instance.ticket.fee
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

		if instance.donation_amount == None:
			instance.donation_amount = decimal.Decimal(10.00)

		# Donation tickets don't have a tiket.fee parameter that we can use
		# so we have to calculate it now
		price_to_calculate = decimal.Decimal(instance.donation_amount)
		# Get the Arqam platform fee from settings
		platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)
		# Get the Arqam platform base fee from settings
		platform_base_fee = decimal.Decimal(settings.PLATFORM_BASE_FEE)
		# Calculate fee
		fee  = decimal.Decimal((price_to_calculate * platform_fee)) + platform_base_fee
		instance.donation_fee = fee
		instance.donation_buyer_amount = price_to_calculate + fee

		instance.ticket_price = price_to_calculate
		instance.ticket_buyer_price = price_to_calculate + fee
		quantity = instance.quantity

		instance.cart_item_total_no_fee = (price_to_calculate * quantity)
		instance.cart_item_total = ((price_to_calculate + fee) * quantity)
		instance.cart_item_fee = (fee * quantity)

		instance.pass_fee = True



def event_cart_item_post_save_reciever(sender, instance, *args, **kwargs):
	instance.event_cart.update_total()

pre_save.connect(event_cart_item_pre_save_reciever, sender=EventCartItem)
post_save.connect(event_cart_item_post_save_reciever, sender=EventCartItem)



