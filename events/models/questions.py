from .base import *
from questions.models import Question  
from events.models import Event, Ticket



# Frequently Asked Attendee Questions --------------------------------------
class AttendeeCommonQuestions(models.Model):
	event = models.OneToOneField(Event, on_delete=models.CASCADE, blank=False, null=False)
	address = models.BooleanField(default=False)
	address_required = models.BooleanField(default=False)
	age = models.BooleanField(default=False)
	age_required = models.BooleanField(default=False)
	gender = models.BooleanField(default=False)
	gender_required = models.BooleanField(default=False)
	country = models.BooleanField(default=False)
	country_required = models.BooleanField(default=False)
	region = models.BooleanField(default=False)
	region_required = models.BooleanField(default=False)
	city = models.BooleanField(default=False)
	city_required = models.BooleanField(default=False)
	email = models.BooleanField(default=False)
	email_required = models.BooleanField(default=False)

	def __str__(self):
		return ("%s" % self.event.title)



def event_post_save_reciever(sender, instance, *args, **kwargs):
	try:
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=instance)
	except:
		AttendeeCommonQuestions.objects.create(event=instance)


post_save.connect(event_post_save_reciever, sender=Event)



class EventQuestion(models.Model):

	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	question = models.OneToOneField(Question, on_delete=models.CASCADE, primary_key=True)
	order_question = models.BooleanField(default=False)
	tickets = models.ManyToManyField(Ticket, blank=True)

	def __str__(self):
		return self.question.title

	def create_question(self):
		view_name = "questions:create_question"
		return reverse(view_name, kwargs={"one_to_one_type": "events", "one_to_one_id": self.event.pk})

	def update_question(self):
		view_name = "questions:update_question"
		return reverse(view_name, kwargs={"one_to_one_type": "events", "one_to_one_id": self.event.pk, "pk": self.pk})

	def view_answers(self):
		view_name = "events:answer_detail"
		return reverse(view_name, kwargs={"slug": self.event.slug, "event_question_id": self.pk})
