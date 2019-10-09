from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin

from houses.mixins import HouseAccountMixin
from houses.models import HouseUser
from events.models import Event, AttendeeCommonQuestions, Ticket, EventQuestion
from questions.models import Question, MultipleChoice
from questions.forms import QuestionForm, MutipleChoiceForm
from questions.mixins import QuestionSecurityMixin




class MultipleChoiceCreateView(HouseAccountMixin, QuestionSecurityMixin, UserPassesTestMixin, CreateView):
	model = MultipleChoice
	form_class = MutipleChoiceForm
	template_name = "questions/multiple_choice_form.html"

	def get_one_to_one_object(self, one_to_one_type, one_to_one_id):
		one_to_one_object = None
		if one_to_one_type == 'events':
			one_to_one_object = Event.objects.get(id=one_to_one_id)
		return one_to_one_object

	def get_question_url(self):
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)

		question = self.get_question()
		view_name = "questions:update_question"
		return reverse(view_name, kwargs={"one_to_one_type": one_to_one_type, "one_to_one_id": one_to_one_id, "pk": question.id})

	def get_success_url(self):
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)

		# Check how many options are already made 
		options = MultipleChoice.objects.filter(question=self.object.question)
		if options.count() < 2:
			view_name = "questions:create_option"
			return reverse(view_name, kwargs={"one_to_one_type": one_to_one_type, "one_to_one_id": one_to_one_id, "pk": self.object.question.id})
		else:
			view_name = "questions:update_question"
			return reverse(view_name, kwargs={"one_to_one_type": one_to_one_type, "one_to_one_id":one_to_one_id, "pk": self.object.question.id})
		

	def get(self, request, *args, **kwargs):
		self.object = None
		return self.render_to_response(self.get_context_data())

	def get_question(self):
		pk = self.kwargs["pk"]
		question = Question.objects.get(id=pk)
		return question

	def get_context_data(self, *args, **kwargs):
		context = {}
		one_to_one_type = self.kwargs['one_to_one_type']
		form = self.get_form()
		context["form"] = form
		context["dashboard_events"] = self.get_events()
		context["question"] = self.get_question()
		context["question_url"] = self.get_question_url()
		return context

	def post(self, request, *args, **kwargs):
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	
	def form_valid(self, form, request):
		data = request.POST
		self.object = form.save(commit=False)
		self.object.question = self.get_question()
		self.object.save()
		self.object.question.save()
		messages.success(request, 'Option added to question successfully!')
		valid_data = super(MultipleChoiceCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))




class MultipleChoiceUpdateView(HouseAccountMixin, QuestionSecurityMixin, UserPassesTestMixin, UpdateView):
	model = MultipleChoice
	form_class = MutipleChoiceForm
	template_name = "questions/multiple_choice_form.html"

	def get_success_url(self):
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)
		view_name = "questions:update_question"
		return reverse(view_name, kwargs={"one_to_one_type": one_to_one_type, "one_to_one_id":one_to_one_id, "pk": self.object.question.id})

	def get_one_to_one_object(self, one_to_one_type, one_to_one_id):
		one_to_one_object = None
		if one_to_one_type == 'events':
			one_to_one_object = Event.objects.get(id=one_to_one_id)
		return one_to_one_object

	def get_option(self):
		pk = self.kwargs["option_id"]
		multiple_choice = MultipleChoice.objects.get(id=pk)
		return multiple_choice

	def get_question(self):
		pk = self.kwargs["pk"]
		question = Question.objects.get(id=pk)
		return question

	def get(self, request, *args, **kwargs):
		self.object = self.get_option()
		return self.render_to_response(self.get_context_data())

	def get_context_data(self, *args, **kwargs):
		context = {}
		form = self.get_form()
		context["option"] = self.object
		context["form"] = form
		context["dashboard_events"] = self.get_events()
		context["update"] = True
		return context

	def post(self, request, *args, **kwargs):
		self.object = self.get_option()
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	
	def form_valid(self, form, request):
		data = request.POST

		if 'delete' in data:
			self.object.deleted = True
			self.object.save()
			self.object.question.save()
			messages.success(request, 'Option Deleted Successfully!')

		elif 'undo-delete' in data:
			self.object.deleted = False
			self.object.save()
			self.object.question.save()
			messages.success(request, 'Option Recovered Successfully!')
		
		else:
			self.object = form.save()
			self.object.question.save()
			messages.success(request, 'Option updated successfully!')

		valid_data = super(MultipleChoiceUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



class QuestionCreateView(HouseAccountMixin, UserPassesTestMixin, CreateView):
	model = Question
	form_class = QuestionForm
	template_name = "questions/question_form.html"

	def test_func(self):
		house_users = HouseUser.objects.filter(profile=self.request.user)
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']

		if one_to_one_type == 'events':
			try:
				event = Event.objects.get(id=self.kwargs['one_to_one_id'])
				for house_user in house_users:
					if event.house == house_user.house:
						return True
				return False
			except:
				raise Http404
		else:
			# Change this when new objects are introduced
			return False

	def get_success_url(self):
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)

		if self.object.question_type == "Multiple Choice":
			view_name = "questions:create_option"
			return reverse(view_name, kwargs={"one_to_one_type": one_to_one_type, "one_to_one_id": one_to_one_id, "pk": self.object.id})
		else:
			view_name = "%s:list_questions" % (one_to_one_type)
			return reverse(view_name, kwargs={"slug": one_to_one_object.slug})


	def get_one_to_one_object(self, one_to_one_type, one_to_one_id):
		one_to_one_object = None
		if one_to_one_type == 'events':
			one_to_one_object = Event.objects.get(id=one_to_one_id)
		else:
			raise Http404
		return one_to_one_object


	def get(self, request, *args, **kwargs):
		self.object = None
		return self.render_to_response(self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}

		form = self.get_form()
		context["form"] = form

		# Get the ticket type from the kwargs
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)


		if one_to_one_type == "events":
			tickets = Ticket.objects.filter(event=one_to_one_object, deleted=False, express=False)
			context["tickets"] = tickets

		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()

		return context


	def post(self, request, *args, **kwargs):
		
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)

		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form, request, one_to_one_type, one_to_one_object)
		else:
			return self.form_invalid(form)


	def form_valid(self, form, request, one_to_one_type, one_to_one_object):

		data = request.POST
		house = self.get_house()
		self.object = form.save()

		self.object.house = house

		if form.cleaned_data['question_type'] == 'simple':
			self.object.question_type = 'simple'

		if one_to_one_type == 'events':
			event_question = EventQuestion.objects.create(event=one_to_one_object, question=self.object)
			if 'order_question' in data:
				event_question.order_question = True
			tickets = Ticket.objects.filter(event=one_to_one_object)
			for ticket in tickets:
				if str(ticket.id) in data:
					event_question.tickets.add(ticket)
			event_question.save()

		messages.success(request, 'Question Created Successfully!')

		valid_data = super(QuestionCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))






class QuestionUpdateView(HouseAccountMixin, QuestionSecurityMixin, UserPassesTestMixin, UpdateView):
	model = Question
	form_class = QuestionForm
	template_name = "questions/question_form.html"


	def create_option_url(self):
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)
		view_name = "questions:create_option"
		return reverse(view_name, kwargs={"one_to_one_type": one_to_one_type, "one_to_one_id":one_to_one_id, "pk":self.object.id})


	def get_success_url(self):
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)
		view_name = "%s:list_questions" % (one_to_one_type)
		return reverse(view_name, kwargs={"slug": one_to_one_object.slug})


	def get_one_to_one_object(self, one_to_one_type, one_to_one_id):
		one_to_one_object = None
		if one_to_one_type == 'events':
			one_to_one_object = Event.objects.get(id=one_to_one_id)
		return one_to_one_object


	def get_question(self, pk):
		question = Question.objects.get(id=pk)
		return question


	def get(self, request, *args, **kwargs):
		pk = self.kwargs['pk']
		self.object = self.get_question(pk)
		return self.render_to_response(self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}

		form = self.get_form()
		context["form"] = form

		# Get the ticket type from the kwargs
		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)
		context["one_to_one_type"] = one_to_one_type
		context["one_to_one_id"] = one_to_one_id

		if one_to_one_type == "events":
			tickets = Ticket.objects.filter(event=one_to_one_object, deleted=False, express=False)
			context["event_question"] = self.object.eventquestion
			context["tickets"] = tickets
			context["event"] = one_to_one_object
			context["event_tab"] = True
			context["dashboard_events"] = self.get_events()


		options = MultipleChoice.objects.filter(question=self.object).order_by("deleted")

		context["options"] = options
		context["question"] = self.object
		context["update"] = True
		context["option_url"] = self.create_option_url()

		return context


	def post(self, request, *args, **kwargs):
		pk = self.kwargs['pk']
		self.object = self.get_question(pk)

		print(request.POST)
		if "delete" in request.POST:
			self.object.deleted = True
			self.object.save()
			HttpResponseRedirect(self.get_success_url())

		one_to_one_type = self.kwargs['one_to_one_type']
		one_to_one_id = self.kwargs['one_to_one_id']
		one_to_one_object = self.get_one_to_one_object(one_to_one_type, one_to_one_id)

		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form, request, one_to_one_type, one_to_one_object)
		else:
			return self.form_invalid(form)


	def form_valid(self, form, request, one_to_one_type, one_to_one_object):

		data = request.POST
		print(data)

		if form.cleaned_data['question_type'] == 'simple':
			self.object.question_type = 'simple'

		self.object = form.save()

		if one_to_one_type == 'events':
			event_question = EventQuestion.objects.get(event=one_to_one_object, question=self.object)
			if 'order_question' in data:
				print("Ye sboss it is coming here")
				event_question.order_question = True
			else:
				event_question.order_question = False
			tickets = Ticket.objects.filter(event=one_to_one_object)
			event_question.tickets.clear()
			for ticket in tickets:
				if str(ticket.id) in data:
					event_question.tickets.add(ticket)
			event_question.save()
			

		messages.success(request, 'Question Updated Successfully!')

		valid_data = super(QuestionUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))






