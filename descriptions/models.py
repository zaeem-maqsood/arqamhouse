from django.db import models
from events.models import Event
from django.urls import reverse




# Create your models here.


# Main description model where events, orders, homepages etc will instantiate from
class Description(models.Model):
	active = models.BooleanField(default=True)



# Event Description Model
class EventDescription(Description):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return self.event.title



# Main description element model, has a foreign key to the description model
class DescriptionElement(models.Model):
	active = models.BooleanField(default=True)
	order = models.PositiveIntegerField(default=1, blank=False, null=False)
	description = models.ForeignKey(Description, on_delete=models.CASCADE, blank=False, null=False)




# --------------------------- Description Elements ------------------------------------------------

class H1Title(DescriptionElement):
	title = models.CharField(max_length=150, null=False, blank=False)

	def __str__(self):
		return str(self.title)



class H2Title(DescriptionElement):
	title = models.CharField(max_length=150, null=False, blank=False)

	def __str__(self):
		return str(self.title)


class H3Title(DescriptionElement):
	title = models.CharField(max_length=150, null=False, blank=False)

	def __str__(self):
		return str(self.title)


class Paragraph(DescriptionElement):
	text = models.TextField(null=False, blank=False)

	def __str__(self):
		return str(self.text)





