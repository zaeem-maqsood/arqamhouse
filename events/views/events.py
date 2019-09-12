from .base import *

import stripe
import decimal
from django.conf import settings
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage

from houses.mixins import HouseAccountMixin
from questions.models import Question
from descriptions.models import EventDescription, DescriptionElement
from events.mixins import EventMixin
from events.models import Event, AttendeeCommonQuestions, EventQuestion, Ticket, EventCart, EventCartItem, Answer, OrderAnswer, EventOrder, Attendee
from events.forms import EventForm, EventCheckoutForm, CheckinForm
from payments.models import Transaction



# Create your views here.



class EventDashboardView(HouseAccountMixin, UserPassesTestMixin, DetailView):
	model = Event
	template_name = "events/event_dashboard.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_tickets(self, event):
		tickets = Ticket.objects.filter(event=event)
		return tickets


	def get_total_sales(self, event):
		orders = EventOrder.objects.filter(event=event, refunded=False).select_related("transaction")
		total_sales = decimal.Decimal(0.00)
		for order in orders:
			if order.transaction.amount:
				total_sales += order.transaction.amount
		return total_sales


	def graph_data(self, event):
		
		today = timezone.now()
		print(today)
		days_earlier = today - timedelta(days=10)
		attendees = Attendee.objects.filter(order__event=event, order__created_at__range=(days_earlier, today), active=True)

		day_label = []
		tickets_label = []

		for x in range(10):
			one_day_earlier = today - timedelta(days=x)
			attendees_for_day = attendees.filter(order__created_at__day=one_day_earlier.day)

			tickets_sum = 0
			for attendee in attendees_for_day:
				tickets_sum += 1

			tickets_label.append("%s" % (tickets_sum))
			day_label.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))

		
		tickets_label = list(reversed(tickets_label))
		day_label = list(reversed(day_label))

		graph_data = {'tickets_label':tickets_label, 'day_label':day_label}
		return graph_data
			

	def get(self, request, *args, **kwargs):


		context = {}
		slug = kwargs['slug']
		house = self.get_house()
		event = self.get_event(slug)

		
		dashboard_events = self.get_events()
		tickets = self.get_tickets(event)

		if event.active == False:
			context["inactive_event_tab"] = True
			context["event_tab"] = False
		else:
			context["event_tab"] = True

		context["tickets"] = tickets
		context["dashboard_events"] = dashboard_events
		context["total_sales"] = self.get_total_sales(event)
		context["graph_data"] = self.graph_data(event)
		context["house"] = house
		context["event"] = event
		context["request"] = request
		return render(request, self.template_name, context)



class EventDescriptionView(HouseAccountMixin, UserPassesTestMixin, EventMixin, ListView):
	model = Event
	template_name = "events/event_description.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_event_description(self, event):
		event_description = EventDescription.objects.get(event=event)
		return event_description

	def get_description_elements(self, event_description):
		description_element = DescriptionElement.objects.filter(description=event_description).order_by("order")
		return description_element


	def get_context_data(self, *args, **kwargs):
		context = {}
		slug = self.kwargs['slug']
		event = self.get_event(slug)
		event_description = self.get_event_description(event)
		description_elements = self.get_description_elements(event_description)

		house = self.get_house()
		context["description_elements"] = description_elements
		context["event"] = event
		context["events_tab"] = True
		context["events"] = self.get_events()
		context["house"] = house
		return context



class EventCheckoutView(FormView):
	template_name = "events/event_checkout_form.html"

	def get_success_url(self):
		view_name = "events:landing"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_cart(self):
		cart_id = self.request.session.get('cart')
		if cart_id:
			cart = EventCart.objects.get(id=cart_id)
		else:
			raise Http404
		return cart



	def get_context_data(self, data=None, *args, **kwargs):
		context = {}

		request = self.request
		slug = self.kwargs['slug']
		event = self.get_event(slug)
		
		cart = self.get_cart()
		cart_items = EventCartItem.objects.filter(event_cart=cart)

		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
		print(attendee_common_questions.age)
			
		context["cart_items"] = cart_items
		context["cart"] = cart
		context["attendee_common_questions"] = attendee_common_questions
		context["event"] = event
		context["public_key"] = settings.STRIPE_PUBLIC_KEY
		context["total"] = cart.total * decimal.Decimal(100.00)
		context["data"] = data
		return context


	def get(self, request, *args, **kwargs):
		# Check if the user should be here in the first place
		cart = self.get_cart()
		cart_items = EventCartItem.objects.filter(event_cart=cart)
		print(cart_items)
		if not cart_items.exists():
			return HttpResponseRedirect(self.get_success_url())

		return render(request, self.template_name, self.get_context_data())


	def post(self, request, *args, **kwargs):
		data = request.POST

		print("STRIPE TOKEN")
		print(data["stripeToken"])
		stripe_token = data["stripeToken"]
		print("\n\n")

		slug = kwargs['slug']
		event = self.get_event(slug)
		cart = self.get_cart()
		print(data)

		# Step 1 Get buyer name and email address
		name = data['name']

		email = data['email']

		transaction = Transaction.objects.create(house=event.house, name=name)
		transaction.save()
		order = EventOrder.objects.create(name=name, email=email, event=event, event_cart=cart, transaction=transaction)
		order.save()

		print("\n")
		print("---------------------------- Buyer name and email")
		print(name)
		print(email)

		# Step 2 Get Buyer questions and make answers
		order_questions = EventQuestion.objects.filter(event=event, order_question=True).order_by("question__order")
		for order_question in order_questions:
			value = data["%s_order_question" % (order_question.question.id)] 

			print("\n")
			print("---------------------------- Order Questions")
			print(value)

			order_answer = OrderAnswer.objects.create(question=order_question, value=value, order=order)
			order_answer.save()


		# Step 3 get answers from attendees 
		cart_items = EventCartItem.objects.filter(event_cart=cart)
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
		

		for cart_item in cart_items:

			attendee_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id).order_by("question__order")

			for quantity in range(cart_item.quantity):

				email = None
				age = None
				gender = None
				note = None
				
				print("\n")
				print("---------------------------- Attendee Common Questions")
				# Step 3a get the name 
				name = data["%s_%s_name" % (quantity, cart_item.ticket.id)]
				print(name)

				# Step 3b answers to common questions
				if attendee_common_questions.email:
					email = data["%s_%s_email" % (quantity, cart_item.ticket.id)]
					print(email)

				if attendee_common_questions.age:
					age = data["%s_%s_age" % (quantity, cart_item.ticket.id)]
					print(age)

				if attendee_common_questions.gender:
					gender = data["%s_%s_gender" % (quantity, cart_item.ticket.id)]
					print(gender) 

				if attendee_common_questions.notes:
					note = data["%s_%s_note" % (quantity, cart_item.ticket.id)]
					print(note)

				
				attendee = Attendee.objects.create(order=order, ticket=cart_item.ticket, name=name, email=email, age=age, gender=gender, note=note)
				attendee.save()

				# Step 3c answers to custom questions
				for attendee_question in attendee_questions:
					value = data["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)]

					print("\n")
					print("---------------------------- Attendee Custom Questions")
					print(value)

					answer = Answer.objects.create(question=attendee_question, value=value, attendee=attendee)
					answer.save()


			
		stripe.api_key = settings.STRIPE_SECRET_KEY
		
		try:
			charge = stripe.Charge.create(
						amount = int(cart.total * 100),
						currency = 'cad',
						description = self.get_charge_description(event, order),
						source = stripe_token,
						statement_descriptor = 'Arqam House Inc.',
					)
			print(charge)

			transaction.amount = cart.total
			transaction.arqam_amount = cart.arqam_charge
			transaction.stripe_amount = cart.stripe_charge
			transaction.house_amount = cart.total_no_fee

			transaction.payment_id = charge['id']
			transaction.failure_code = charge['failure_code']
			transaction.failure_message = charge['failure_message']
			transaction.last_four = charge.source['last4']
			transaction.brand = charge.source['brand']
			transaction.network_status = charge.outcome['network_status']
			transaction.reason = charge.outcome['reason']
			transaction.risk_level = charge.outcome['risk_level']
			transaction.seller_message = charge.outcome['seller_message']
			transaction.outcome_type = charge.outcome['type']
			transaction.email = data['email']
			transaction.name = charge.source['name']
			transaction.address_line_1 = charge.source['address_line1']
			transaction.address_state = charge.source['address_state']
			transaction.address_postal_code = charge.source['address_zip']
			transaction.address_city = charge.source['address_city']
			transaction.address_country = charge.source['address_country']
			transaction.save()

			cart.processed = True
			cart.update_tickets_available()
			cart.save()
			del request.session['cart']
			request.session.modified = True
			messages.success(request, 'Check your email for tickets and further instructions.')

			return HttpResponseRedirect(self.get_success_url())

		except Exception as e:
			print(e)
			order.failed = True
			transaction.failed = True
			transaction.code_fail_reason = "Order Failed Due to Exception: %s" % (e)
			order.save()
			transaction.save()
			cart.processed = False
			cart.save()
			del request.session['cart']
			request.session.modified = True
			messages.error(request, 'There was an error in proccessing your payment card. Please try again with a different payment card.')
			return HttpResponseRedirect(self.get_success_url())


		return render(request, self.template_name, self.get_context_data(data))



	def get_charge_description(self, event, order):
		return ("Order #: %s for Event: %s (Event ID: %s)." % (order.id, event.title, event.id))


	def get_charge_descriptor(self, event):
		event_title = event.title
		if len(event_title) > 20:
			descriptor = event.house.name
			if len(descriptor) > 20:
				descriptor = 'Arqam House Inc.'
		else:
			descriptor = event_title
		return descriptor





class EventLandingView(DetailView):
	model = Event
	template_name = "events/event_landing.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_event_description(self, event):
		event_description = EventDescription.objects.get(event=event)
		return event_description

	def get_description_elements(self, event_description):
		description_elements = DescriptionElement.objects.filter(description=event_description)
		return description_elements

	def get(self, request, *args, **kwargs):
		context = {}
		slug = kwargs['slug']
		
		event = self.get_event(slug)
		event_description = self.get_event_description(event)
		description_elements = self.get_description_elements(event_description)

		context["event_description"] = event_description
		context["description_elements"] = description_elements
		context["event"] = event
		context["tickets"] = event.ticket_set.filter(sold_out=False).exists()
		context["request"] = request
		return render(request, self.template_name, context)




class PastEventsView(HouseAccountMixin, UserPassesTestMixin, EventMixin, ListView):
	model = Event
	template_name = "events/past_events.html"


	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		inactive_events = self.get_inactive_events(house=house)
		deleted_events = self.get_deleted_events(house=house)
		context["events"] = inactive_events
		context["deleted_events"] = deleted_events
		context["house"] = house
		context["dashboard_events"] = self.get_events()
		context["past_event_tab"] = True
		return context



class EventCreateView(HouseAccountMixin, UserPassesTestMixin, CreateView):
	model = Event
	form_class = EventForm
	template_name = "events/event_form.html"

	def get_success_url(self):
		house = self.get_house()
		view_name = "houses:dashboard"
		return reverse(view_name, kwargs={'slug': house.slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		house = self.get_house()
		context["form"] = form
		context["house"] = house
		context["create_event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST
		house = self.get_house()
		form.instance.house = house
		self.object = form.save()
		self.object.active = True
		self.object.save()

		# Create the event description object 
		event_description = EventDescription.objects.create(event=self.object)
		event_description.save()

		messages.success(request, 'Event Published')
		valid_data = super(EventCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



class EventUpdateView(HouseAccountMixin, UserPassesTestMixin, UpdateView):
	model = Event
	form_class = EventForm
	template_name = "events/event_form.html"

	def get_success_url(self):
		view_name = "events:update"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_success_delete_url(self):
		view_name = "events:past"
		return reverse(view_name)

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		house = self.get_house()
		context["form"] = form
		context["house"] = house
		context["event"] = self.object
		
		if self.object.active == False:
			context["inactive_event_tab"] = True
			context["events_tab"] = False
		else:
			context["events_tab"] = True

		context["update_event"] = True

		if self.object.active:
			context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		print(self.get_events())
		return context

	def get(self, request, *args, **kwargs):
		slug = kwargs['slug']
		self.object = self.get_event(slug)
		form = EventForm(instance=self.object, initial={"start": self.object.start.strftime("%m/%d/%Y %I:%M %p"), "end": self.object.end.strftime("%m/%d/%Y %I:%M %p")})
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		slug = kwargs['slug']
		self.object = self.get_event(slug)
		data = request.POST

		# Undoing a deletion of an event
		if "Undo Delete" in data:
			self.object.deleted = False
			self.object.save()
			return HttpResponseRedirect(self.get_success_url())

		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST
		self.object = form.save()

		if "Archive" in data:
			self.object.active = False
			self.object.save()
			messages.warning(request, 'Archived Event')

		if "Remove" in data:
			self.object.image = None
			self.object.save()
			messages.warning(request, 'Event Image Removed')

		if "Re-Open" in data:
			self.object.active = True
			self.object.save()
			messages.info(request, 'Event Re-Opened')

		if "Delete" in data:
			self.object.active = False
			self.object.deleted = True
			self.object.save()
			messages.warning(request, 'Event Deleted Successfully')
			return HttpResponseRedirect(self.get_success_delete_url())

		messages.success(request, 'Event Updated')
		valid_data = super(EventUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))





