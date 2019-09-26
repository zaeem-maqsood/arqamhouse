from .base import *
from django.conf import settings
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from houses.mixins import HouseAccountMixin

from events.forms import FreeTicketForm, PaidTicketForm, DonationTicketForm
from events.models import Event, Ticket



# Create your views here.

class TicketListView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, ListView):
	model = Ticket
	template_name = "events/tickets/list_tickets.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
		except:
			raise Http404
		return event

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		event = self.get_event(self.kwargs['slug'])
		tickets = Ticket.objects.filter(event=event).order_by("deleted")
		print(tickets)
		context["tickets"] = tickets
		context["event"] = event
		context["dashboard_events"] = self.get_events()
		context["house"] = house
		context["event_tab"] = True
		return context




class TicketCreateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, CreateView):
	model = Ticket
	form_class = None
	template_name = "events/tickets/create_ticket.html"
	button_text = "Create Ticket"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
		except:
			raise Http404
		return event

	def get_success_url(self):
		view_name = "events:list_tickets"
		return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

	def get_context_data(self, form, ticket_type, event, *args, **kwargs):
		context = {}
		house = self.get_house()

		if ticket_type == "free":
			context["free_ticket"] = True
		elif ticket_type == "paid":
			context["paid_ticket"] = True
		elif ticket_type == "donation":
			context["donation_ticket"] = True
		else:
			form = None

		platform_fee = settings.PLATFORM_FEE
		platform_base_fee = settings.PLATFORM_BASE_FEE

		context["platform_fee"] = platform_fee
		context["platform_base_fee"] = platform_base_fee
		context["button_text"] = self.button_text
		context["form"] = form
		context["ticket_type"] = ticket_type
		context["house"] = house
		context["event"] = event
		context["dashboard_events"] = self.get_events()
		context["event_tab"] = True
		return context

	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])

		self.object = None

		# Get the ticket type from the kwargs
		ticket_type = kwargs['type']
		if ticket_type == "free":
			self.form_class = FreeTicketForm
			form = self.get_form()
		elif ticket_type == "paid":
			self.form_class = PaidTicketForm
			form = self.get_form()
		elif ticket_type == "donation":
			self.form_class = DonationTicketForm
			form = self.get_form()
		else:
			form = None


		return self.render_to_response(self.get_context_data(form=form, ticket_type=ticket_type, event=event))

	def post(self, request, *args, **kwargs):
		
		data = request.POST

		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])

		# Get the ticket type from the kwargs
		ticket_type = kwargs['type']
		if ticket_type == "free":
			self.form_class = FreeTicketForm
			form = self.get_form()
		elif ticket_type == "paid":
			self.form_class = PaidTicketForm
			form = self.get_form()
		elif ticket_type == "donation":
			self.form_class = DonationTicketForm
			form = self.get_form()
		else:
			form = None
			raise Http404

		
		if form.is_valid():
			return self.form_valid(form, request, event, ticket_type)
		else:
			return self.form_invalid(form, ticket_type, event)

	def form_valid(self, form, request, event, ticket_type):
		data = request.POST

		form.instance.event = event

		title = form.cleaned_data.get("title")
		price = form.cleaned_data.get("price")
		sale_price = form.cleaned_data.get("sale_price")

		if ticket_type == "free":
			form.instance.free = True
		elif ticket_type == "paid":
			form.instance.paid = True
		elif ticket_type == "donation":	
			form.instance.donation = True

		form.instance.price = price
		form.instance.sale_price = sale_price

		self.object = form.save()

		messages.success(request, 'Ticket %s Created Successfully!' % (title))

		valid_data = super(TicketCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, ticket_type, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, ticket_type=ticket_type, event=event))





class TicketUpdateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):
	model = Ticket
	form_class = None
	template_name = "events/tickets/create_ticket.html"
	button_text = "Update Ticket"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
		except Exception as e:
			print(e)
			raise Http404
		return event

	def get_ticket(self, event, ticket_slug):
		try:
			ticket = Ticket.objects.get(event=event, slug=ticket_slug)
		except Exception as e:
			print(e)
			raise Http404
		return ticket

	def get_success_url(self):
		view_name = "events:list_tickets"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_context_data(self, form, ticket, event, *args, **kwargs):
		context = {}
		house = self.get_house()

		if ticket.free == True:
			context["free_ticket"] = True
		elif ticket.paid == True:
			context["paid_ticket"] = True
		elif ticket.donation == True:
			context["donation_ticket"] = True
		else:
			form = None

		platform_fee = settings.PLATFORM_FEE
		platform_base_fee = settings.PLATFORM_BASE_FEE

		context["platform_fee"] = platform_fee
		context["platform_base_fee"] = platform_base_fee
		context["button_text"] = self.button_text
		context["form"] = form
		context["ticket"] = ticket
		context["house"] = house
		context["event"] = event
		context["dashboard_events"] = self.get_events()
		context["event_tab"] = True
		return context

	def get(self, request, *args, **kwargs):
		
		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])
		ticket = self.get_ticket(event, kwargs['ticket_slug'])

		self.object = ticket

		# Get the ticket type from the kwargs
		if ticket.free == True:
			self.form_class = FreeTicketForm
			form = self.get_form()
		elif ticket.paid == True:
			form = PaidTicketForm(instance=self.object)
		elif ticket.donation == True:
			self.form_class = DonationTicketForm
			form = self.get_form()
		else:
			form = None


		return self.render_to_response(self.get_context_data(form=form, ticket=ticket, event=event))

	def post(self, request, *args, **kwargs):
		
		data = request.POST

		# Check to make sure event slug is correct
		event = self.get_event(kwargs['slug'])
		ticket = self.get_ticket(event, kwargs['ticket_slug'])

		self.object = ticket

		# Get the ticket type from the kwargs
		if ticket.free == True:
			self.form_class = FreeTicketForm
			form = self.get_form()
		elif ticket.paid == True:
			self.form_class = PaidTicketForm
			form = self.get_form()
		elif ticket.donation == True:
			self.form_class = DonationTicketForm
			form = self.get_form()
		else:
			form = None
		
		if form.is_valid():
			return self.form_valid(form, request, event, ticket)
		else:
			return self.form_invalid(form, ticket, event)

	def form_valid(self, form, request, event, ticket):
		data = request.POST

		form.instance.event = event

		price = form.cleaned_data.get("price")
		sale_price = form.cleaned_data.get("sale_price")

		if "delete" in data:
			self.object.deleted = True
			self.object.save()
			messages.success(request, 'Ticket Deleted Successfully!')

		elif 'undo-delete' in data:
			self.object.deleted = False
			self.object.save()
			messages.success(request, 'Ticket Recovered Successfully!')

		else:
			form.instance.price = price
			form.instance.sale_price = sale_price
			self.object = form.save()
			messages.success(request, 'Ticket Updated Successfully!')


		valid_data = super(TicketUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form, ticket, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, ticket=ticket, event=event))





