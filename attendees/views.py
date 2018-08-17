import stripe
from django.conf import settings
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages

from organizations.mixins import OrganizationAccountMixin
from .models import Attendee
from events.models import Event


# Create your views here.
class AttendeeListView(OrganizationAccountMixin, ListView):
	model = Attendee
	template_name = "attendees/event_attendees.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def get_context_data(self, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		event = self.get_event(self.kwargs['slug'])
		attendees = Attendee.objects.filter(order__event=event)
		print(attendees)
		
		context["organization"] = organization
		context["attendees"] = attendees
		context["event"] = event
		return context