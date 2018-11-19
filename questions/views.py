from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages

from organizations.mixins import OrganizationAccountMixin
from events.models import Event, EventGeneralQuestions, AttendeeGeneralQuestions
from tickets.models import Ticket
from .models import (EventQuestion, TicketQuestion, EventQuestionMultipleChoiceOption, AllTicketQuestionControl, 
					TicketQuestionMultipleChoiceOption, AllTicketQuestionMultipleChoiceOption)
from .forms import (EventQuestionBaseForm, EventGeneralQuestionsForm, AttendeeGeneralQuestionsForm, 
					EventQuestionMutipleChoiceOptionForm, AllTicketQuestionForm, TicketQuestionForm,
					AllTicketQuestionMutipleChoiceOptionForm, TicketQuestionMutipleChoiceOptionForm)

# Create your views here.





# Generic functions

# Get Event Function
def get_event(slug):
	try:
		event = Event.objects.get(slug=slug)
	except Exception as e:
		print(e)
		raise Http404
	return event

# Get question type to display template properly
def get_question_type(question_type, context):

	if question_type == "simple":
		context["simple"] = True
	elif question_type == "paragraph":
		context["paragraph"] = True
	elif question_type == "mutiple choice":
		context["multiple_choice"] = True
	else:
		raise Http404

	return context



class QuestionsListView(OrganizationAccountMixin, View):

	template_name = "events/questions/list_questions.html"

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())


	def post(self, request, *args, **kwargs):
		
		event = get_event(self.kwargs['slug'])

		event_general_questions_instance = EventGeneralQuestions.objects.get(event=event)
		attendee_general_questions_instance = AttendeeGeneralQuestions.objects.get(event=event)

		event_general_questions_form = EventGeneralQuestionsForm(instance=event_general_questions_instance, data=request.POST)
		attendee_general_questions_form = AttendeeGeneralQuestionsForm(instance=attendee_general_questions_instance, data=request.POST)
		if event_general_questions_form.is_valid() and attendee_general_questions_form.is_valid():

			event_general_questions_instance = event_general_questions_form.save()
			attendee_general_questions_instance = attendee_general_questions_form.save()

			event_general_questions_instance.save()
			attendee_general_questions_instance.save()

			messages.success(request, 'Questions Updated Successfully!')
			return render(request, self.template_name, self.get_context_data())

		else:
			return render(request, self.template_name, self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		event = get_event(self.kwargs['slug'])

		event_general_questions_instance = EventGeneralQuestions.objects.get(event=event)
		attendee_general_questions_instance = AttendeeGeneralQuestions.objects.get(event=event)

		event_general_questions_form = EventGeneralQuestionsForm(instance=event_general_questions_instance)
		attendee_general_questions_form = AttendeeGeneralQuestionsForm(instance=attendee_general_questions_instance)

		event_questions = EventQuestion.objects.filter(event=event, deleted=False).order_by('order')
		all_ticket_questions = AllTicketQuestionControl.objects.filter(event=event, deleted=False).order_by('order')
		ticket_questions = TicketQuestion.objects.filter(event=event, ticket__isnull=False, deleted=False).order_by('order')

		context["tickets"] = Ticket.objects.filter(event=event, deleted=False)
		context["event_general_questions_form"] = event_general_questions_form
		context["attendee_general_questions_form"] = attendee_general_questions_form
		context["event_questions"] = event_questions
		context["all_ticket_questions"] = all_ticket_questions
		context["ticket_questions"] = ticket_questions
		context["event"] = event
		context["organization"] = organization
		context["events_tab"] = True
		context["active_event_tab"] = True
		return context






# Functions for the following for Classes 
def get_ticket(ticket_slug):
	try:
		ticket = Ticket.objects.get(slug=ticket_slug)
	except:
		raise Http404
	return ticket


# This view creates questions for specific tickets 
class TicketQuestionCreateView(OrganizationAccountMixin, CreateView):
	model = TicketQuestion
	form_class = TicketQuestionForm
	template_name = "events/questions/create_question.html"

	# Check if multiple choice question then bring user back to question to add options 
	# Else got back to list questions
	def get_success_url(self):
		if self.kwargs['type'] == "multiple choice":
			view_name = "events:questions:update_ticket_question"
			return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.object.slug, "ticket_slug": self.kwargs['ticket_slug']})
		else:
			view_name = "events:questions:list_questions"
			return reverse(view_name, kwargs={"slug": self.kwargs['slug']})


	def get_context_data(self, form, question_type, event, ticket, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context = get_question_type(question_type, context)
		context["ticket"] = ticket
		context["form"] = form
		context["question_type"] = question_type
		context["organization"] = organization
		context["event"] = event
		context["events_tab"] = True
		return context


	def post(self, request, *args, **kwargs):
		
		data = request.POST

		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])
		ticket = get_ticket(kwargs['ticket_slug'])

		# Get the ticket type from the kwargs
		question_type = kwargs['type']
		form = self.get_form()

		
		if form.is_valid():
			return self.form_valid(form, request, event, question_type, ticket)
		else:
			return self.form_invalid(form, question_type, event, ticket)


	def form_valid(self, form, request, event, question_type, ticket):
		data = request.POST

		form.instance.event = event
		form.instance.ticket = ticket

		title = form.cleaned_data.get("title")

		if question_type == "simple":
			form.instance.simple_question = True
		elif question_type == "paragraph":
			form.instance.paragraph_question = True
		elif question_type == "multiple choice":
			form.instance.multiple_choice_question = True
		else:
			pass

		self.object = form.save()

		messages.success(request, 'Question "%s" Created Successfully!' % (title))

		valid_data = super(TicketQuestionCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question_type, event, ticket):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question_type=question_type, event=event, ticket=ticket))


	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])
		ticket = get_ticket(kwargs['ticket_slug'])

		self.object = None

		# Get the ticket type from the kwargs
		question_type = kwargs['type']
		form = self.get_form()

		return self.render_to_response(self.get_context_data(form=form, question_type=question_type, event=event, ticket=ticket))



# Get Ticket Object Question
# Used for the next three classes 
def get_ticket_question(event, ticket, question_slug):
	try:
		question = TicketQuestion.objects.get(event=event, ticket=ticket, slug=question_slug)
	except Exception as e:
		print(e)
	return question


class TicketQuestionUpdateView(OrganizationAccountMixin, UpdateView):
	model = TicketQuestion
	form_class = TicketQuestionForm
	template_name = "events/questions/create_question.html"

	# Success url
	def get_success_url(self):
		view_name = "events:questions:list_questions"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	# Context variables
	def get_context_data(self, form, question, event, ticket, *args, **kwargs):
		context = {}
		organization = self.get_organization()

		if question.simple_question:
			context["simple"] = True
		elif question.paragraph_question:
			context["paragraph"] = True
		elif question.multiple_choice_question:
			context["multiple_choice"] = True
			ticket_question_multiple_choice_options = TicketQuestionMultipleChoiceOption.objects.filter(ticket_question=question, deleted=False)
			context["event_question_multiple_choice_options"] = ticket_question_multiple_choice_options
		else:
			pass

		context["ticket"] = ticket
		context["form"] = form
		context["question"] = question
		context["organization"] = organization
		context["event"] = event
		context["events_tab"] = True
		context["update"] = True
		context["single_ticket"] = True
		return context


	def post(self, request, *args, **kwargs):

		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])
		ticket = get_ticket(kwargs['ticket_slug'])
		question = get_ticket_question(event, ticket, kwargs['question_slug'])

		# Set question to object
		self.object = question

		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question, ticket)
		else:
			return self.form_invalid(form, question, event, ticket)


	def form_valid(self, form, request, event, question, ticket):
		# Get post data
		data = request.POST

		title = form.cleaned_data.get("title")

		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.success(request, 'Question %s Deleted Successfully!' % (title))

		else:
			form.instance.event = event
			form.instance.ticket = ticket
			form.instance.all_ticket_question_control = None
			self.object = form.save()
			messages.success(request, 'Question "%s" Updated Successfully!' % (title))
		
		valid_data = super(TicketQuestionUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question, event, ticket):
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event, ticket=ticket))


	def get(self, request, *args, **kwargs):
		
		# Get event ticket and question object
		event = get_event(kwargs['slug'])
		ticket = get_ticket(kwargs['ticket_slug'])
		question = get_ticket_question(event, ticket, kwargs['question_slug'])

		# Set object to question
		self.object = question

		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event, ticket=ticket))





class TicketQuestionMultipleChoiceOptionUpdateView(OrganizationAccountMixin, UpdateView):
	model = TicketQuestionMultipleChoiceOption
	form_class = TicketQuestionMutipleChoiceOptionForm
	template_name = "events/questions/create_option.html"

	def get_context_data(self, form, question, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()

		context["form"] = form
		context["organization"] = organization
		context["event"] = event
		context["question"] = question
		context["update"] = True
		context["events_tab"] = True
		context["single_ticket"] = True
		return context

	def get_success_url(self):
		view_name = "events:questions:update_ticket_question"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.kwargs['question_slug'], "ticket_slug": self.object.ticket_question.ticket.slug})


	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
		except Exception as e:
			print(e)
			raise Http404
		return event

	def get_question(self, event, ticket, question_slug):
		try:
			question = TicketQuestion.objects.get(event=event, ticket=ticket, slug=question_slug)
		except Exception as e:
			print(e)
			raise Http404
		return question

	def get_ticket(self, ticket_slug):
		try:
			ticket = Ticket.objects.get(slug=ticket_slug)
		except Exception as e:
			print(e)
			raise Http404
		return ticket

	def get_option(self, event, question, option_slug):
		try:
			option = TicketQuestionMultipleChoiceOption.objects.get(ticket_question__event=event, ticket_question=question, slug=option_slug)
		except Exception as e:
			print(e)
			raise Http404
		return option


	def form_valid(self, form, request, event, question):
		data = request.POST
		title = form.cleaned_data.get("title")
		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.success(request, 'Option "%s" Deleted Successfully!' % (title))
		else:
			form.instance.event_question = question
			self.object = form.save()
			messages.success(request, 'Option "%s" Updated Successfully!' % (title))
		valid_data = super(TicketQuestionMultipleChoiceOptionUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))

	def post(self, request, *args, **kwargs):
		
		data = request.POST

		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])
		ticket = self.get_ticket(kwargs['ticket_slug'])
		question = self.get_question(event, ticket, kwargs['question_slug'])
		option = self.get_option(event, question, kwargs['option_slug'])
		self.object = option

		form = self.get_form()
	
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)

	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])
		ticket = self.get_ticket(kwargs['ticket_slug'])
		question = self.get_question(event, ticket, kwargs['question_slug'])
		option = self.get_option(event, question, kwargs['option_slug'])
		self.object = option

		# Get the ticket type from the kwargs
		form = self.get_form()

		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))




class TicketQuestionMultipleChoiceOptionCreateView(OrganizationAccountMixin, CreateView):
	model = TicketQuestionMultipleChoiceOption
	form_class = TicketQuestionMutipleChoiceOptionForm
	template_name = "events/questions/create_option.html"

	def get_context_data(self, form, question, event, ticket, *args, **kwargs):
		context = {}
		organization = self.get_organization()

		context["form"] = form
		context["organization"] = organization
		context["event"] = event
		context["question"] = question
		context["ticket"] = ticket
		context["events_tab"] = True
		context["single_ticket"] = True
		return context

	def get_success_url(self):
		view_name = "events:questions:update_ticket_question"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.kwargs['question_slug'], "ticket_slug": self.kwargs['ticket_slug']})

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
		except Exception as e:
			print(e)
			raise Http404
		return event

	def get_question(self, event, ticket, question_slug):
		try:
			question = TicketQuestion.objects.get(event=event, ticket=ticket, slug=question_slug)
		except Exception as e:
			print(e)
			raise Http404
		return question


	def get_ticket(self, ticket_slug):
		try:
			ticket = Ticket.objects.get(slug=ticket_slug)
		except Exception as e:
			print(e)
			raise Http404
		return ticket


	def form_valid(self, form, request, event, question, ticket):
		data = request.POST

		form.instance.ticket_question = question
		form.instance.ticket_question.ticket = ticket
		form.instance.ticket_question.all_ticket_question_control = None

		title = form.cleaned_data.get("title")
		self.object = form.save()

		messages.success(request, 'Option "%s" Created Successfully!' % (title))

		valid_data = super(TicketQuestionMultipleChoiceOptionCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question, event, ticket):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event, ticket=ticket))

	def post(self, request, *args, **kwargs):
		
		data = request.POST

		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])
		ticket = self.get_ticket(kwargs['ticket_slug'])
		question = self.get_question(event, ticket, kwargs['question_slug'])

		form = self.get_form()
	
		if form.is_valid():
			return self.form_valid(form, request, event, question, ticket)
		else:
			return self.form_invalid(form, question, event, ticket)

	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])
		ticket = self.get_ticket(kwargs['ticket_slug'])
		question = self.get_question(event, ticket, kwargs['question_slug'])
		self.object = None

		# Get the ticket type from the kwargs
		form = self.get_form()

		return self.render_to_response(self.get_context_data(form=form, question=question, event=event, ticket=ticket))







































# This view controls the creation of all ticket questions 
class AllTicketQuestionCreateView(OrganizationAccountMixin, CreateView):
	
	model = AllTicketQuestionControl
	form_class = AllTicketQuestionForm
	template_name = "events/questions/create_question.html"

	# success url takes user back to question list view or brings them back to add options if multiple 
	# choice question
	def get_success_url(self):

		if self.kwargs['type'] == "multiple choice":
			view_name = "events:questions:update_all_ticket_question"
			return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.object.slug})

		else:
			view_name = "events:questions:list_questions"
			return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_context_data(self, form, question_type, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context = get_question_type(question_type, context)
		context["all_ticket_question"] = True
		context["form"] = form
		context["question_type"] = question_type
		context["organization"] = organization
		context["event"] = event
		context["events_tab"] = True
		context["all_ticket"] = True
		return context

	def post(self, request, *args, **kwargs):

		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])

		# Get the ticket type from the kwargs
		question_type = kwargs['type']
		
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question_type)
		else:
			return self.form_invalid(form, question_type, event)


	def form_valid(self, form, request, event, question_type):
		# add the event instance to the object 
		form.instance.event = event

		# Get the title for the success message
		title = form.cleaned_data.get("title")

		# Set the question type on the object retrieved from the kwargs
		if question_type == "simple":
			form.instance.simple_question = True
		elif question_type == "paragraph":
			form.instance.paragraph_question = True
		elif question_type == "multiple choice":
			form.instance.multiple_choice_question = True
		else:
			pass

		# Save Object
		self.object = form.save()

		# Success Message
		messages.success(request, 'Question "%s" Created Successfully!' % (title))
		valid_data = super(AllTicketQuestionCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question_type, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question_type=question_type, event=event))


	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])

		# Object set to none for creation
		self.object = None

		# Get the ticket type from the kwargs
		question_type = kwargs['type']
		
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question_type=question_type, event=event))



# Get All Ticket Question function reused for the following three classes 
def get_all_ticket_question(event, question_slug):
	try:
		question = AllTicketQuestionControl.objects.get(event=event, slug=question_slug)
	except:
		raise Http404
	return question



# This view updates the all ticket question models 
class AllTicketQuestionUpdateView(OrganizationAccountMixin, UpdateView):
	
	model = AllTicketQuestionControl
	form_class = AllTicketQuestionForm
	template_name = "events/questions/create_question.html"

	# Success url take them back to questions list
	def get_success_url(self):
		view_name = "events:questions:list_questions"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})


	# Get question type to display template properly
	def get_question_type(self, question, context):

		if question.simple_question:
			context["simple"] = True
		elif question.paragraph_question:
			context["paragraph"] = True
		elif question.multiple_choice_question:
			# Get all options associated with this question
			all_ticket_question_multiple_choice_options = AllTicketQuestionMultipleChoiceOption.objects.filter(all_ticket_question=question, deleted=False)
			context["event_question_multiple_choice_options"] = all_ticket_question_multiple_choice_options
			context["multiple_choice"] = True
		else:
			raise Http404

		return context

	# Context variables
	def get_context_data(self, form, question, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context = self.get_question_type(question, context)
		context["all_ticket_question"] = True
		context["form"] = form
		context["question"] = question
		context["organization"] = organization
		context["event"] = event
		context["events_tab"] = True
		context["update"] = True
		context["all_ticket"] = True
		return context


	def post(self, request, *args, **kwargs):

		# Get event and question objects
		event = get_event(kwargs['slug'])
		question = get_all_ticket_question(event, kwargs['question_slug'])

		# Set the object to the question
		self.object = question

		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)


	def form_valid(self, form, request, event, question):
		# Get POST data
		data = request.POST

		# Get title for success message
		title = form.cleaned_data.get("title")

		# Check if delete in post data, if so set object to deleted
		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.warning(request, 'Question %s Deleted Successfully!' % (title))

		# If not deleted update object
		else:
			form.instance.event = event
			self.object = form.save()
			messages.success(request, 'Question "%s" Updated Successfully!' % (title))
		
		valid_data = super(AllTicketQuestionUpdateView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))


	def get(self, request, *args, **kwargs):
		
		# Get event and question object
		event = get_event(kwargs['slug'])
		question = get_all_ticket_question(event, kwargs['question_slug'])

		# Set object to qquestion instance 
		self.object = question

		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))



# This view creates options for the multiple choice question type
class AllTicketQuestionMultipleChoiceOptionCreateView(OrganizationAccountMixin, CreateView):
	model = AllTicketQuestionMultipleChoiceOption
	form_class = AllTicketQuestionMutipleChoiceOptionForm
	template_name = "events/questions/create_option.html"

	# Context Variables
	def get_context_data(self, form, question, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context["all_ticket_question"] = True
		context["form"] = form
		context["organization"] = organization
		context["event"] = event
		context["question"] = question
		context["events_tab"] = True
		context["all_ticket"] = True
		return context

	# Get success url
	def get_success_url(self):
		view_name = "events:questions:update_all_ticket_question"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.kwargs['question_slug']})


	def form_valid(self, form, request, event, question):

		# Set all ticket question to the object instance 
		form.instance.all_ticket_question = question

		# Get the option title for the success message
		title = form.cleaned_data.get("title")
		
		# Save object
		self.object = form.save()

		# Success message
		messages.success(request, 'Option "%s" Created Successfully!' % (title))
		valid_data = super(AllTicketQuestionMultipleChoiceOptionCreateView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))


	def post(self, request, *args, **kwargs):

		# Get event and question 
		event = get_event(kwargs['slug'])
		question = get_all_ticket_question(event, kwargs['question_slug'])

		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)

	def get(self, request, *args, **kwargs):
		
		# Get event and question
		event = get_event(kwargs['slug'])
		question = get_all_ticket_question(event, kwargs['question_slug'])
		
		# Set object to none
		self.object = None

		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))


# This view updates the options associated with multiple choice questions
class AllTicketQuestionMultipleChoiceOptionUpdateView(OrganizationAccountMixin, UpdateView):
	model = AllTicketQuestionMultipleChoiceOption
	form_class = AllTicketQuestionMutipleChoiceOptionForm
	template_name = "events/questions/create_option.html"

	# Context variables
	def get_context_data(self, form, question, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context["all_ticket_question"] = True
		context["form"] = form
		context["organization"] = organization
		context["event"] = event
		context["question"] = question
		context["update"] = True
		context["events_tab"] = True
		context["all_ticket"] = True
		return context

	# Take user back to question on success
	def get_success_url(self):
		view_name = "events:questions:update_all_ticket_question"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.kwargs['question_slug']})

	# Get the option from the kwargs
	def get_option(self, event, question, option_slug):
		try:
			option = AllTicketQuestionMultipleChoiceOption.objects.get(all_ticket_question__event=event, all_ticket_question=question, slug=option_slug)
		except Exception as e:
			print(e)
			raise Http404
		return option

	def form_valid(self, form, request, event, question):
		# Get the post data
		data = request.POST

		# Get the title from the form for the success message
		title = form.cleaned_data.get("title")

		# Check if delete in data, if so then set option to deleted
		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.warning(request, 'Option "%s" Deleted Successfully!' % (title))

		# If not deleted then update option
		else:
			form.instance.event_question = question
			self.object = form.save()
			messages.success(request, 'Option "%s" Updated Successfully!' % (title))
		valid_data = super(AllTicketQuestionMultipleChoiceOptionUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))

	def post(self, request, *args, **kwargs):

		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])
		question = get_all_ticket_question(event, kwargs['question_slug'])
		option = self.get_option(event, question, kwargs['option_slug'])
		
		# Set the object to the option
		self.object = option

		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)

	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])
		question = get_all_ticket_question(event, kwargs['question_slug'])
		option = self.get_option(event, question, kwargs['option_slug'])
		
		# set the option object
		self.object = option

		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))





































# Event Question Create View 
# Takes in organization mixin for authentication 
class EventQuestionCreateView(OrganizationAccountMixin, CreateView):
	model = EventQuestion
	form_class = EventQuestionBaseForm
	template_name = "events/questions/create_question.html"

	# Success URL
	def get_success_url(self):

		# If the question being created is a multiple choice question bring them back to the question page because
		# we want them to app options right away
		if self.kwargs['type'] == "multiple choice":
			view_name = "events:questions:update_event_question"
			return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.object.slug})

		# If not multiple choice question take user back to questions view
		else:
			view_name = "events:questions:list_questions"
			return reverse(view_name, kwargs={"slug": self.kwargs['slug']})


	# Get context data for template
	def get_context_data(self, form, question_type, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context = get_question_type(question_type, context)
		context["event_question"] = True 
		context["form"] = form
		context["question_type"] = question_type
		context["organization"] = organization
		context["event"] = event
		context["events_tab"] = True
		return context


	def post(self, request, *args, **kwargs):

		# Get event
		event = get_event(kwargs['slug'])

		# Get the ticket type from the kwargs
		question_type = kwargs['type']
		
		# CreateView mixin handles form
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question_type)
		else:
			return self.form_invalid(form, question_type, event)


	def form_valid(self, form, request, event, question_type):

		# set event to question instance
		form.instance.event = event

		# get title of question for display message
		title = form.cleaned_data.get("title")

		# Set question type boolen based off of question type
		if question_type == "simple":
			form.instance.simple_question = True
		elif question_type == "paragraph":
			form.instance.paragraph_question = True
		elif question_type == "multiple choice":
			form.instance.multiple_choice_question = True
		else:
			pass

		# Save object
		self.object = form.save()

		# Success Message
		messages.success(request, 'Question "%s" Created Successfully!' % (title))
		valid_data = super(EventQuestionCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question_type, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question_type=question_type, event=event))


	def get(self, request, *args, **kwargs):
		
		# Get event
		event = get_event(kwargs['slug'])

		# set object to None
		self.object = None

		# Get the ticket type from the kwargs
		question_type = kwargs['type']
		form = self.get_form()

		return self.render_to_response(self.get_context_data(form=form, question_type=question_type, event=event))




# Event Question Update View 
# Takes in organization mixin for authentication 
class EventQuestionUpdateView(OrganizationAccountMixin, UpdateView):
	
	model = EventQuestion
	form_class = EventQuestionBaseForm
	template_name = "events/questions/create_question.html"

	# Success url, takes user back to question list view
	def get_success_url(self):
		view_name = "events:questions:list_questions"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})


	# Get question from event instance and slug
	def get_question(self, event, question_slug):
		try:
			question = EventQuestion.objects.get(event=event, slug=question_slug)
		except:
			raise Http404
		return question


	# Get question type to display template properly
	def get_question_type(self, question, context):

		if question.simple_question:
			context["simple"] = True
		elif question.paragraph_question:
			context["paragraph"] = True
		elif question.multiple_choice_question:
			# Get all options associated with this question
			event_question_multiple_choice_options = EventQuestionMultipleChoiceOption.objects.filter(event_question=question, deleted=False)
			context["event_question_multiple_choice_options"] = event_question_multiple_choice_options
			context["multiple_choice"] = True
		else:
			raise Http404

		return context


	# Context Data for template
	def get_context_data(self, form, question, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()

		# Get the question type and send it to the template 
		context = self.get_question_type(question, context)

		context["event_question"] = True 
		context["form"] = form
		context["question"] = question
		context["organization"] = organization
		context["event"] = event
		context["events_tab"] = True
		context["update"] = True
		return context


	def post(self, request, *args, **kwargs):
		
		data = request.POST

		# Retrieve Event and question from kwargs 
		event = get_event(kwargs['slug'])
		question = self.get_question(event, kwargs['question_slug'])

		# Set current object to question instance
		self.object = question

		# UpdateView mixin handles form
		form = self.get_form()	
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)


	def form_valid(self, form, request, event, question):
		data = request.POST

		# Get the question title, only needs for the success message
		title = form.cleaned_data.get("title")

		# Check if delete value in post data, if so delete object
		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.warning(request, 'Question "%s" Deleted Successfully!' % (title))

		# save event instance to question, save the form, present success message
		else:
			form.instance.event = event
			self.object = form.save()
			messages.success(request, 'Question "%s" Updated Successfully!' % (title))
		
		valid_data = super(EventQuestionUpdateView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))


	def get(self, request, *args, **kwargs):
		
		# Retrieve Event and question from kwargs 
		event = get_event(kwargs['slug'])
		question = self.get_question(event, kwargs['question_slug'])

		# Set current object to question instance
		self.object = question

		# UpdateView mixin handles form
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))



# Get question function for Event Multiple Choice Create View and Update view 
def get_event_question(question_slug):
	try:
		question = EventQuestion.objects.get(slug=question_slug)
	except:
		raise Http404
	return question


# Event Multiple Choice Option Create View
class EventQuestionMultipleChoiceOptionCreateView(OrganizationAccountMixin, CreateView):
	model = EventQuestionMultipleChoiceOption
	form_class = EventQuestionMutipleChoiceOptionForm
	template_name = "events/questions/create_option.html"

	def get_success_url(self):
		view_name = "events:questions:update_event_question"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.kwargs['question_slug']})

	def form_valid(self, form, request, event, question):

		# Add event question instance to option 
		form.instance.event_question = question

		# get the title of the option from the form
		title = form.cleaned_data.get("title")

		# Save the form
		self.object = form.save()

		# Success message
		messages.success(request, 'Option "%s" Created Successfully!' % (title))

		valid_data = super(EventQuestionMultipleChoiceOptionCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))

	def post(self, request, *args, **kwargs):

		# Check to make sure event slug is correct
		event = get_event(kwargs['slug'])

		# Get event question
		question = get_event_question(kwargs['question_slug'])

		# Create View handles the form
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)

	def get(self, request, *args, **kwargs):
		
		# Get event
		event = get_event(kwargs['slug'])

		# Get event question
		question = get_event_question(kwargs['question_slug'])
		
		# Set object to none because we are creating a new one
		self.object = None

		# Form handled by create view
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))



# Event Question Multiple Choice Option Update View 
class EventQuestionMultipleChoiceOptionUpdateView(OrganizationAccountMixin, CreateView):
	model = EventQuestionMultipleChoiceOption
	form_class = EventQuestionMutipleChoiceOptionForm
	template_name = "events/questions/create_option.html"

	# Context data
	def get_context_data(self, form, question, event, *args, **kwargs):
		context = {}
		organization = self.get_organization()

		context["event_question"] = True 
		context["form"] = form
		context["organization"] = organization
		context["event"] = event
		context["question"] = question
		context["update"] = True
		context["events_tab"] = True
		return context

	def get_success_url(self):
		view_name = "events:questions:update_event_question"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "question_slug": self.kwargs['question_slug']})

	# Get the option object to update
	def get_option(self, option_slug):
		try:
			option = EventQuestionMultipleChoiceOption.objects.get(slug=option_slug)
		except:
			raise Http404
		return option

	def form_valid(self, form, request, event, question):

		# Get the POST data
		data = request.POST

		# Get title of option from form data for success message
		title = form.cleaned_data.get("title")

		# Check if delete in data and if so then delete the option
		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.warning(request, 'Option "%s" Deleted Successfully!' % (title))

		# If not delete save updated option
		else:
			form.instance.event_question = question
			self.object = form.save()
			messages.success(request, 'Option "%s" Updated Successfully!' % (title))

		valid_data = super(EventQuestionMultipleChoiceOptionUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, question, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))

	def post(self, request, *args, **kwargs):

		# get event and question object
		event = get_event(kwargs['slug'])
		question = get_event_question(kwargs['question_slug'])

		# Get option object
		option = self.get_option(kwargs['option_slug'])

		# Set the option object 
		self.object = option

		# Form handled by update view 
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event, question)
		else:
			return self.form_invalid(form, question, event)

	def get(self, request, *args, **kwargs):

		event = get_event(kwargs['slug'])
		question = get_event_question(kwargs['question_slug'])

		# Get option object
		option = self.get_option(kwargs['option_slug'])
		self.object = option

		# Get the ticket type from the kwargs
		form = self.get_form()

		return self.render_to_response(self.get_context_data(form=form, question=question, event=event))





































