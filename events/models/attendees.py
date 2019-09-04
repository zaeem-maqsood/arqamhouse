from .base import *

from core.models import TimestampedModel
from events.models import Ticket, EventOrder, EventCartItem
from core.constants import genders
from cities_light.models import City, Region, Country
from payments.models import Refund


class Attendee(TimestampedModel):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	name = models.CharField(max_length=150, null=True, blank=True)
	email = models.EmailField(max_length=120, null=True, blank=True)
	note = models.TextField(blank=True, null=True)
	gender = models.CharField(max_length=20, choices=genders, default='female', null=True, blank=True)
	age = models.PositiveSmallIntegerField(blank=True, null=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name


	def get_attendee_view(self):
		view_name = "events:attendee_detail"
		return reverse(view_name, kwargs={"slug": self.order.event.slug, "attendee_id": self.id})



class EventOrderRefund(models.Model):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	refund = models.ForeignKey(Refund, on_delete=models.CASCADE, blank=True, null=True)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return (self.order.name)


