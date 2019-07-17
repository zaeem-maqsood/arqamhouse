import stripe
from django.conf import settings
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string

from houses.mixins import HouseAccountMixin
from .models import Attendee
from events.models import Event

from .forms import AttendeeForm
from answers.models import TicketAnswer
from questions.models import TicketQuestion



# Generic functions

# Get Event Function
def get_event(slug):
	try:
		event = Event.objects.get(slug=slug)
	except Exception as e:
		print(e)
		raise Http404
	return event


# Create your views here.
class AttendeeListView(HouseAccountMixin, ListView):
	model = Attendee
	template_name = "attendees/event_attendees.html"

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)
		event = self.get_event(self.kwargs['slug'])
		all_attendees = Attendee.objects.filter(order__event=event).order_by('order__created_at')
		search_terms = data["search"].split()

		if data["search"] == '':
			attendees = all_attendees
		else:
			counter = 0
			for search_term in search_terms:
				if counter == 0:
					attendees = all_attendees.filter(Q(name__icontains=search_term) | Q(ticket__title__icontains=search_term))
				else:
					attendees = attendees.filter(Q(name__icontains=search_term) | Q(ticket__title__icontains=search_term))
				print(counter)
				counter += 1
		
		attendees = attendees[:100]
		print(attendees)
		html = render_to_string('attendees/attendees-dynamic-table-body.html', {'attendees': attendees, 'request':request})
		return HttpResponse(html)

	def get_context_data(self, *args, **kwargs):
		context = {}
		House = self.get_House()
		event = get_event(self.kwargs['slug'])
		attendees = Attendee.objects.filter(order__event=event)
		print(attendees)
		
		context["House"] = House
		context["attendees"] = attendees
		context["event"] = event
		context["events_tab"] = True
		context["events"] = self.get_events()
		return context




class AttendeeDetailView(HouseAccountMixin, FormView):
	model = Attendee
	template_name = "attendees/event_attendees_detail.html"

	def get_success_url(self):
		view_name = "events:attendees:detail"

		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "attendee_slug": self.kwargs['attendee_slug']})

	def get_attendee(self, attende_slug):
		try:
			attendee = Attendee.objects.get(slug=attende_slug)
			return attendee
		except Exception as e:
			print(e)
			raise Http404

	def get_context_data(self, event, attendee, request, form, *args, **kwargs):
		context = {}
		context["event"] = event
		context["attendee"] = attendee
		context["questions"] = TicketQuestion.objects.filter(event=event)
		context["form"] = form
		context["events_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):
		context = {}
		slug = kwargs['slug']
		attendee_slug = kwargs['attendee_slug']
		event = get_event(slug)
		attendee = self.get_attendee(attendee_slug)
		answers = TicketAnswer.objects.filter(attendee=attendee)
		data = {}
		for answer in answers:
			data["%s_question" % (answer.question.id)] = answer.value
		form = AttendeeForm(event=event, initial=data, instance=attendee)
		return self.render_to_response(self.get_context_data(event=event, request=request, attendee=attendee, form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		attendee_slug = kwargs['attendee_slug']
		event = get_event(slug)
		attendee = self.get_attendee(attendee_slug)

		form = AttendeeForm(event=event, initial=data, instance=attendee, data=data)
		if form.is_valid():
			messages.success(request, 'Attendee updated successfully!')
			return self.form_valid(form, request, event, attendee)
		else:
			messages.warning(request, 'Oops! Something went wrong.')
			return self.form_invalid(form, request, event, attendee)

	def form_valid(self, form, request, event, attendee):
		questions = TicketQuestion.objects.filter(event=event)
		answers = TicketAnswer.objects.filter(attendee=attendee)

		name = form.cleaned_data['name']
		gender = form.cleaned_data['gender']
		email = form.cleaned_data['email']

		attendee.name = name
		attendee.gender = gender
		attendee.email = email

		attendee.save()

		for question in questions:
			value = form.cleaned_data['%s_question' % (question.id)]
			print(value)
			if str(value) is not None:
				print(value)
				answer = TicketAnswer.objects.create(attendee=attendee, question=question, value=value)
				answer.save()
				print(answer)
		valid_data = super(AttendeeDetailView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, request, event, attendee):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, request=request, event=event, attendee=attendee))








