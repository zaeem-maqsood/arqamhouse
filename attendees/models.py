from django.db import models

from orders.models import Order, EventOrder
from tickets.models import Ticket
from core.constants import genders


# Create your models here.

class Attendee(models.Model):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	name = models.CharField(max_length=150, null=True, blank=True)
	email = models.EmailField(max_length=120, null=True, blank=True)
	gender = models.CharField(max_length=20, choices=genders, default='female', null=True, blank=True)

	def __str__(self):
		return self.first_name