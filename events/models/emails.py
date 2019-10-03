from .base import *
from events.models import Event, AttendeeCommonQuestions


class EventEmailConfirmation(models.Model):

	event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)
	message = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.event.title





# Create these with every event
def event_post_save_reciever(sender, instance, *args, **kwargs):
	try:
		AttendeeCommonQuestions.objects.get(event=instance)
	except:
		AttendeeCommonQuestions.objects.create(event=instance)

	try:
		# Check if email conf exists
		EventEmailConfirmation.objects.get(event=instance)
	except:
		# Create Email Confirmation object
		EventEmailConfirmation.objects.create(event=instance)


post_save.connect(event_post_save_reciever, sender=Event)
