from django.db import models

from questions.models import EventQuestion, TicketQuestion
from attendees.models import Attendee
from orders.models import Order, EventOrder

# Create your models here.

class Answer(models.Model):
	value = models.CharField(max_length=300, null=True, blank=True)



class EventAnswer(Answer):
	question = models.ForeignKey(EventQuestion, on_delete=models.CASCADE, blank=False, null=False)
	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return ("%s" % self.value)


class TicketAnswer(Answer):
	question = models.ForeignKey(TicketQuestion, on_delete=models.CASCADE, blank=False, null=False)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return ("%s" % self.value)