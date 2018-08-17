from django.db import models
from django.urls import reverse
from events.models import Event
from carts.models import EventCart


# Create your models here.
class Order(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
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


class EventOrder(Order):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	event_cart = models.ForeignKey(EventCart, on_delete=models.CASCADE, blank=False, null=False)
	email = models.EmailField(max_length=300, blank=False, null=False)
	note = models.TextField(blank=True, null=True)

	def __str__(self):
		return ("%s" % self.event.title)

	def get_order_view(self):
		view_name = "events:orders:detail"
		return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})

	