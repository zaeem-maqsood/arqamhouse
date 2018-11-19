from django.db import models
from events.models import Event



# Create your models here.
class Payout(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2)




class EventPayout(Payout):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)


	def __str__(self):
		return ("%s" % self.event.title)