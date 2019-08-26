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
from events.models import Event, Attendee, Answer, AttendeeCommonQuestions

from events.forms import AttendeeForm


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
	template_name = "events/attendees/event_attendees.html"

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
		html = render_to_string('events/attendees/attendees-dynamic-table-body.html', {'attendees': attendees, 'request':request})
		return HttpResponse(html)

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		event = get_event(self.kwargs['slug'])
		attendees = Attendee.objects.filter(order__event=event, order__failed=False)
		print(attendees)
		
		context["house"] = house
		context["attendees"] = attendees
		context["event"] = event
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context




class AttendeeDetailView(HouseAccountMixin, FormView):
	model = Attendee
	template_name = "events/attendees/event_attendees_detail.html"

	def get_success_url(self):
		view_name = "events:attendee_detail"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "attendee_id": self.kwargs['attendee_id']})

	def get_attendee(self, attende_id):
		try:
			attendee = Attendee.objects.get(id=attende_id)
			return attendee
		except Exception as e:
			print(e)
			raise Http404

	def get_context_data(self, *args, **kwargs):
		context = {}

		house = self.get_house()
		slug = self.kwargs['slug']
		attendee_id = self.kwargs['attendee_id']
		event = get_event(slug)
		attendee = self.get_attendee(attendee_id)
		answers = Answer.objects.filter(attendee=attendee)
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
		print(attendee_common_questions.age)

		context["house"] = house
		context["attendee_common_questions"] = attendee_common_questions
		context["event"] = event
		context["attendee"] = attendee
		context["answers"] = answers
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):
		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		attendee_id = kwargs['attendee_id']
		event = get_event(slug)
		attendee = self.get_attendee(attendee_id)
		answers = Answer.objects.filter(attendee=attendee)

		if 'name' in data:
			attendee.name = data['name']
			attendee.save()

		if 'email' in data:
			attendee.email = data['email']
			attendee.save()

		if 'gender' in data:
			attendee.gender = data['gender']
			attendee.save()

		if 'age' in data:
			attendee.age = data['age']
			attendee.save()

		if 'note' in data:
			attendee.note = data['note']
			attendee.save()

		for answer in answers:
			value = data["%s_%s" % (answer.question.pk, answer.attendee.id)]
			answer.value = value
			answer.save()

		messages.success(request, 'Attendee Updated')

		return self.render_to_response(self.get_context_data())







