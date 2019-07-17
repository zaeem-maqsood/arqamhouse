import random
import string
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from events.models import Event
from events.models import Ticket


# Create your models here.

# Base Question Model
class Question(models.Model):

	title = models.CharField(max_length=100, null=True, blank=True)
	order = models.PositiveSmallIntegerField(blank=True, null=False, default=1)
	help_text = models.CharField(max_length=150, null=True, blank=True)
	required = models.BooleanField(default=False)
	simple_question = models.BooleanField(default=False)
	paragraph_question = models.BooleanField(default=False)
	multiple_choice_question = models.BooleanField(default=False)
	slug = models.SlugField(max_length = 375, unique = False, blank=True)
	deleted = models.BooleanField(default=False)
	approved = models.BooleanField(default=True)





# Event Question Model
class EventQuestion(Question):

	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	question = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
	value = models.CharField(max_length=200, null=True, blank=True)
	

	def __str__(self):
		return self.title


	def set_approval(self):
		if self.multiple_choice_question:
			options = EventQuestionMultipleChoiceOption.objects.filter(event_question=self, deleted=False)
			if options.count() < 2:
				self.approved = False
				self.save()
			else:
				self.approved = True
				self.save()


	def update_event_question_view(self):
		view_name = "events:questions:update_event_question"
		return reverse(view_name, kwargs={"slug": self.event.slug, "question_slug": self.slug})


	def create_event_multiple_choice_question_option_view(self):
		view_name = "events:questions:create_multiple_choice_option"
		return reverse(view_name, kwargs={"slug": self.event.slug, "question_slug": self.slug})


def create_slug(instance):

	slug = slugify(instance.title)
	slug = slug + '-%s' % (instance.id)
	return slug


def event_question_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_slug(instance)

def event_question_post_save_reciever(sender, instance, *args, **kwargs):
	if instance.multiple_choice_question:
		options = EventQuestionMultipleChoiceOption.objects.filter(event_question=instance, deleted=False)
		if options.count() < 2:
			instance.approved = False
		else:
			instance.approved = True

pre_save.connect(event_question_pre_save_reciever, sender=EventQuestion)
post_save.connect(event_question_post_save_reciever, sender=EventQuestion)






class EventQuestionMultipleChoiceOption(models.Model):
	event_question = models.ForeignKey(EventQuestion, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=200, null=True, blank=True)
	slug = models.SlugField(max_length = 375, unique = False, blank=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def update_event_muliple_choice_question_option_view(self):
		view_name = "events:questions:update_multiple_choice_option"
		return reverse(view_name, kwargs={"slug": self.event_question.event.slug, "question_slug": self.event_question.slug, "option_slug":self.slug})

def create_event_question_multiple_choice_option_slug(instance, new_slug=None):

	slug = slugify(instance.title)
	slug = slug + '-%s' % (instance.id)
	return slug

def event_question_multiple_choice_option_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_event_question_multiple_choice_option_slug(instance)

def event_question_multiple_choice_option_post_save_reciever(sender, instance, *args, **kwargs):
	instance.event_question.set_approval()

pre_save.connect(event_question_multiple_choice_option_pre_save_reciever, sender=EventQuestionMultipleChoiceOption)
post_save.connect(event_question_multiple_choice_option_post_save_reciever, sender=EventQuestionMultipleChoiceOption)








class AllTicketQuestionControl(Question):

	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return self.title

	def set_approval(self):
		if self.multiple_choice_question:
			options = AllTicketQuestionMultipleChoiceOption.objects.filter(all_ticket_question=self, deleted=False)
			if options.count() < 2:
				self.approved = False
				self.save()
			else:
				self.approved = True
				self.save()


	def update_all_ticket_question_view(self):
		view_name = "events:questions:update_all_ticket_question"
		return reverse(view_name, kwargs={"slug": self.event.slug, "question_slug": self.slug})

	def create_all_ticket_multiple_choice_question_option_view(self):
		view_name = "events:questions:create_all_ticket_multiple_choice_option"
		return reverse(view_name, kwargs={"slug": self.event.slug, "question_slug": self.slug})


	def remove_and_add_ticket_question(self):

		# Remove all existing ticket questions
		TicketQuestion.objects.filter(all_ticket_question_control=self).delete()

		# Based off of new data create new ticket questions
		event = self.event
		tickets = Ticket.objects.filter(event=event)
		for ticket in tickets:
			ticket_question = TicketQuestion.objects.create(all_ticket_question_control=self, event=self.event, ticket=ticket, 
				title=self.title, order=self.order, help_text=self.help_text, required=self.required,
				simple_question=self.simple_question, paragraph_question=self.paragraph_question, multiple_choice_question=self.multiple_choice_question)


		ticket_questions = TicketQuestion.objects.filter(all_ticket_question_control=self)
		for question in ticket_questions:
			question.clean_slug()
			question.save()
			if self.multiple_choice_question:
				all_ticket_question_multiple_choice_options = AllTicketQuestionMultipleChoiceOption.objects.filter(all_ticket_question=self)
				for option in all_ticket_question_multiple_choice_options:
					ticket_multiple_choice_option = TicketQuestionMultipleChoiceOption.objects.create(ticket_question=question, title=option.title)





def all_ticket_question_control_create_slug(instance):

	slug = slugify(instance.title)
	slug = slug + '-%s' % (instance.id)
	return slug


def all_ticket_question_control_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = all_ticket_question_control_create_slug(instance)


def all_ticket_question_control_post_save_reciever(sender, instance, *args, **kwargs):
	instance.remove_and_add_ticket_question()


post_save.connect(all_ticket_question_control_post_save_reciever, sender=AllTicketQuestionControl)
pre_save.connect(all_ticket_question_control_pre_save_reciever, sender=AllTicketQuestionControl)




class AllTicketQuestionMultipleChoiceOption(models.Model):
	all_ticket_question = models.ForeignKey(AllTicketQuestionControl, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=200, null=True, blank=True)
	slug = models.SlugField(max_length = 375, unique = False, blank=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def update_all_ticket_muliple_choice_question_option_view(self):
		view_name = "events:questions:update_all_ticket_multiple_choice_option"
		return reverse(view_name, kwargs={"slug": self.all_ticket_question.event.slug, "question_slug": self.all_ticket_question.slug, "option_slug":self.slug})

	def remove_and_add_ticket_option(self):
		ticket_questions = TicketQuestion.objects.filter(all_ticket_question_control=self.all_ticket_question)
		for question in ticket_questions:
			ticket_question_multiple_choice_options = TicketQuestionMultipleChoiceOption.objects.filter(ticket_question=question).delete()
			ticket_question_multiple_choice_option = TicketQuestionMultipleChoiceOption.objects.create(ticket_question=ticket_question, title=self.title)



def create_all_ticket_question_multiple_choice_option_slug(instance):
	slug = slugify(instance.title)
	slug = slug + '-%s' % (instance.id)
	return slug


def all_ticket_question_multiple_choice_option_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_all_ticket_question_multiple_choice_option_slug(instance)

def all_ticket_question_multiple_choice_option_post_save_reciever(sender, instance, *args, **kwargs):
	instance.all_ticket_question.set_approval()

pre_save.connect(all_ticket_question_multiple_choice_option_pre_save_reciever, sender=AllTicketQuestionMultipleChoiceOption)
post_save.connect(all_ticket_question_multiple_choice_option_post_save_reciever, sender=AllTicketQuestionMultipleChoiceOption)










class TicketQuestion(Question):

	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	all_ticket_question_control = models.ForeignKey(AllTicketQuestionControl, on_delete=models.CASCADE, blank=True, null=True)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return ("%s - %s" % (self.title, self.ticket))

	def clean_slug(self):
		slug = slugify(self.title)
		slug = slug + '-%s' % (self.id)
		return slug


	def set_approval(self):
		if self.multiple_choice_question:
			options = TicketQuestionMultipleChoiceOption.objects.filter(ticket_question=self, deleted=False)
			if options.count() < 2:
				self.approved = False
				self.save()
			else:
				self.approved = True
				self.save()

	
	def update_ticket_question_view(self):
		view_name = "events:questions:update_ticket_question"
		return reverse(view_name, kwargs={"slug": self.event.slug, "question_slug": self.slug, "ticket_slug":self.ticket.slug})


	def create_ticket_multiple_choice_question_option_view(self):
		view_name = "events:questions:create_ticket_multiple_choice_option"
		return reverse(view_name, kwargs={"slug": self.event.slug, "question_slug": self.slug, "ticket_slug": self.ticket.slug})


def create_ticket_question_slug(instance):

	slug = slugify(instance.title)
	slug = slug + '-%s' % (instance.id)
	return slug


def ticket_question_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_ticket_question_slug(instance)


def ticket_question_post_save_reciever(sender, instance, *args, **kwargs):
	if instance.multiple_choice_question:
		options = TicketQuestionMultipleChoiceOption.objects.filter(ticket_question=instance, deleted=False)
		if options.count() < 2:
			instance.approved = False
		else:
			instance.approved = True

pre_save.connect(ticket_question_pre_save_reciever, sender=TicketQuestion)
post_save.connect(ticket_question_pre_save_reciever, sender=TicketQuestion)






class TicketQuestionMultipleChoiceOption(models.Model):
	ticket_question = models.ForeignKey(TicketQuestion, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=200, null=True, blank=True)
	slug = models.SlugField(max_length = 375, unique = False, blank=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def update_ticket_muliple_choice_question_option_view(self):
		view_name = "events:questions:update_ticket_multiple_choice_option"
		return reverse(view_name, kwargs={"slug": self.ticket_question.event.slug, "question_slug": self.ticket_question.slug, "ticket_slug":self.ticket_question.ticket.slug, "option_slug":self.slug})


def create_ticket_question_multiple_choice_option_slug(instance, new_slug=None):

	slug = slugify(instance.title)
	slug = slug + '-%s' % (instance.id)
	return slug

def ticket_question_multiple_choice_option_pre_save_reciever(sender, instance, *args, **kwargs):
	instance.slug = create_ticket_question_multiple_choice_option_slug(instance)

def ticket_question_multiple_choice_option_post_save_reciever(sender, instance, *args, **kwargs):
	instance.ticket_question.set_approval()

pre_save.connect(ticket_question_multiple_choice_option_pre_save_reciever, sender=TicketQuestionMultipleChoiceOption)
post_save.connect(ticket_question_multiple_choice_option_post_save_reciever, sender=TicketQuestionMultipleChoiceOption)





# Order Question Model



# Subscription Question Model




# Campaign Question Model

