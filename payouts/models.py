from django.db import models
from organizations.models import Organization
from events.models import Event
from django.urls import reverse



# Create your models here.
class Payout(models.Model):

	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2)


	def get_absolute_url(self):
		view_name = "payouts:detail"
		return reverse(view_name, kwargs={"pk": self.id})


class EventPayout(Payout):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)


	def __str__(self):
		return ("%s" % self.event.title)