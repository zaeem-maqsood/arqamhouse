from .base import *
from .questions import EventQuestion
from .attendees import Attendee
from .orders import EventOrder



class OrderAnswer(models.Model):
	question = models.ForeignKey(EventQuestion, on_delete=models.CASCADE, blank=False, null=False)
	value = models.CharField(max_length=300, null=True, blank=True)
	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return (self.order.name)


class Answer(models.Model):

	question = models.ForeignKey(EventQuestion, on_delete=models.CASCADE, blank=False, null=False)
	value = models.CharField(max_length=300, null=True, blank=True)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return (self.attendee.name)
