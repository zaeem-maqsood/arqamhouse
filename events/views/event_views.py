from .base_views import *

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
from django.utils.timezone import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage

from houses.mixins import HouseAccountMixin
from questions.models import EventQuestion, AllTicketQuestionControl, TicketQuestion
from answers.models import EventAnswer, TicketAnswer
from carts.models import EventCart, EventCartItem
from attendees.models import Attendee
from orders.models import EventOrder
from descriptions.models import EventDescription, DescriptionElement
from events.mixins import EventMixin
from events.models import Event, EventGeneralQuestions, AttendeeGeneralQuestions, Checkin, Ticket
from events.forms import EventForm, EventCheckoutForm, CheckinForm




# Create your views here.



class EventDashboardView(HouseAccountMixin, DetailView):
	model = Event
	template_name = "events/event_dashboard.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404


	def get_attendees(self, event):
		attendees = Attendee.objects.filter(order__event=event).select_related("order", "ticket", "order__event").prefetch_related("order", "ticket", "order__event")
		return attendees

	def get_tickets(self, event):
		tickets = Ticket.objects.filter(event=event)
		return tickets

	def get_all_ticket_and_sales_data(self, attendees):
		order_ids = set()
		tickets_sum = 0
		sales_sum = decimal.Decimal(0.00)
		order_sum = 0
		for attendee in attendees:
			tickets_sum += 1
			if not int(attendee.order.id) in order_ids:
				order_ids.add(attendee.order.id)
				order_sum += 1
				sales_sum += attendee.order.amount

		data = {"tickets_sum": tickets_sum, "sales_sum": sales_sum, "order_sum": order_sum}
		return data


	def get_ten_day_ticket_and_sales_data(self, attendees):

		# Get Todays Date
		now = datetime.today()

		# Get 15 days earlier date
		fifteen_days_earlier = now - timedelta(days=10)

		# Filter all attendees to only 15 days
		attendees = attendees.filter(order__created_at__range=(fifteen_days_earlier, now))

		# Day label for both graphs
		day_label = []

		# 10 days sales label
		sales_label = []

		# 10 days tickets label
		tickets_label = []

		# Booleans to use a large scale or not
		use_large_scale_tickets = False
		use_large_scale = False

		# Calculate sales and ticket labels 
		today = datetime.today()
		for x in range(10):
			one_day_earlier = today - timedelta(days=x)
			attendees_for_day = attendees.filter(order__created_at__day=one_day_earlier.day)
			order_ids = set()
			sales_sum = decimal.Decimal(0.00)
			tickets_sum = 0
			for attendee in attendees_for_day:
				tickets_sum += 1
				if tickets_sum > 20:
					use_large_scale_tickets = True

				if not int(attendee.order.id) in order_ids:
					order_ids.add(attendee.order.id)
					sales_sum += attendee.order.amount
					if sales_sum > 20:
						use_large_scale = True

			sales_label.append("%.2f" % sales_sum)
			tickets_label.append("%s" % (tickets_sum))	
			day_label.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))

		sales_label = list(reversed(sales_label))
		day_label = list(reversed(day_label))
		tickets_label = list(reversed(tickets_label))

		data = {"tickets_label":tickets_label, "sales_label": sales_label, "day_label": day_label, "use_large_scale": use_large_scale, "use_large_scale_tickets":use_large_scale_tickets}
		return data



	def get(self, request, *args, **kwargs):

		# send_mail('subject', 'body of the message', 'info@arqamhouse.com', ['zaeem@arqamhouse.com'])
		# Test
		# attendee = Attendee.objects.get(id=2110)
		# context_dict = {}
		# context_dict["attendee"] = attendee
		# html_string = render_to_string('pdfs/ticket.html', context_dict)
		# css_string = render_to_string('pdfs/ticket.css')
		# html = HTML(string=html_string)
		# css_styles = CSS(string=css_string)
		# css_bootstrap = CSS(url="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css")
		# attendee.pdf = SimpleUploadedFile(attendee.name +'.pdf', html.write_pdf(stylesheets=[css_bootstrap, css_styles]), content_type='application/pdf')
		# attendee.save()


		context = {}
		slug = kwargs['slug']
		house = self.get_house()
		print(house.get_dashboard_url)
		event = self.get_event(slug)
		events = self.get_events()
		tickets = self.get_tickets(event)
		attendees = self.get_attendees(event)
		all_ticket_and_sales_data = self.get_all_ticket_and_sales_data(attendees)
		get_ten_day_ticket_and_sales_data = self.get_ten_day_ticket_and_sales_data(attendees)

		if event.active == False:
			context["inactive_event_tab"] = True
			context["events_tab"] = False
		else:
			context["events_tab"] = True

		context["attendees"] = attendees
		context["tickets"] = tickets
		context["dashboard_events"] = events
		context["all_ticket_and_sales_data"] = all_ticket_and_sales_data
		context["get_ten_day_ticket_and_sales_data"] = get_ten_day_ticket_and_sales_data
		context["house"] = house
		context["event"] = event
		context["request"] = request
		return render(request, self.template_name, context)



class EventDescriptionView(HouseAccountMixin, EventMixin, ListView):
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
	template_name = "events/event_checkout.html"

	def get_success_url(self):
		view_name = "events:landing"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})


	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_context_data(self, form, event, request, *args, **kwargs):
		context = {}
		
		cart_id = request.session.get('cart')
		if cart_id:
			cart = EventCart.objects.get(id=cart_id)
		else:
			raise Http404

		cart_items = EventCartItem.objects.filter(event_cart=cart)
		event_questions = EventQuestion.objects.filter(event=event, deleted=False, approved=True).order_by('order')
		ticket_questions = TicketQuestion.objects.filter(event=event, deleted=False, approved=True).order_by('order')
		event_general_questions = EventGeneralQuestions.objects.get(event=event)
		attendee_general_questions = AttendeeGeneralQuestions.objects.get(event=event)


		all_cart_items = []
		for cart_item in cart_items:
			for x in range(cart_item.quantity):
				cart_item_dict = {}
				cart_item_dict["cart_item"] = cart_item
				cart_item_dict["quantity"] = x
				all_cart_items.append(cart_item_dict)
			
		

		context["event_general_questions"] = event_general_questions
		context["attendee_general_questions"] = attendee_general_questions
		context["cart_items"] = cart_items
		context["all_cart_items"] = all_cart_items
		context["event_questions"] = event_questions
		context["ticket_questions"] = ticket_questions
		context["form"] = form
		context["cart"] = cart
		context["event"] = event
		context["events_tab"] = True
		context["public_key"] = settings.STRIPE_PUBLIC_KEY
		print(settings.STRIPE_PUBLIC_KEY)
		context["total"] = cart.total * decimal.Decimal(100.00)
		return context


	def get(self, request, *args, **kwargs):
		context = {}

		slug = kwargs['slug']
		event = self.get_event(slug)

		cart_id = request.session.get('cart')
		if cart_id:
			cart = EventCart.objects.get(id=cart_id)
		else:
			raise Http404

		form = EventCheckoutForm(event=event, cart=cart)
		print(form)

		return self.render_to_response(self.get_context_data(form=form, event=event, request=request))

	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		event = self.get_event(slug)

		cart_id = request.session.get('cart')
		if cart_id:
			cart = EventCart.objects.get(id=cart_id)
		else:
			raise Http404

		form = EventCheckoutForm(event=event, cart=cart, data=data)
		token = data["token"]
		print(token)
		if form.is_valid():
			return self.form_valid(form, request, event, cart, token)
		else:
			return self.form_invalid(form, request, event)

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

	def form_valid(self, form, request, event, cart, token):


		if token:
			# Create Order
			order = EventOrder.objects.create(house=event.house, event=event, event_cart=cart)

			stripe.api_key = settings.STRIPE_SECRET_KEY

			try:
				charge = stripe.Charge.create(
							amount = int(cart.total * 100),
							currency = 'cad',
							description = self.get_charge_description(event, order),
							source = token,
							statement_descriptor = self.get_charge_descriptor(event),
						)

				print(charge)
				# Assign Values given by stripe to order object 
				order.amount = (int(charge['amount']) / 100)
				order.payment_id = charge['id']
				order.failure_code = charge['failure_code']
				order.failure_message = charge['failure_message']
				order.last_four = charge.source['last4']
				order.brand = charge.source['brand']
				order.network_status = charge.outcome['network_status']
				order.reason = charge.outcome['reason']
				order.risk_level = charge.outcome['risk_level']
				order.seller_message = charge.outcome['seller_message']
				order.outcome_type = charge.outcome['type']
				order.email = form.cleaned_data.get("email")
				order.name = charge.source['name']
				order.address_line_1 = charge.source['address_line1']
				order.address_state = charge.source['address_state']
				order.address_postal_code = charge.source['address_zip']
				order.address_city = charge.source['address_city']
				order.address_country = charge.source['address_country']
				order.save()

				event_questions = EventQuestion.objects.filter(event=event, deleted=False, approved=True).order_by('order')
				ticket_questions = TicketQuestion.objects.filter(event=event, deleted=False, approved=True).order_by('order')
				cart_items = EventCartItem.objects.filter(event_cart=cart)

				# Get Attendee General Questions
				attendee_general_questions = AttendeeGeneralQuestions.objects.get(event=event)

				# Save Event Questions
				for question in event_questions:
					value = form.cleaned_data['%s_eventquestion' % (question.id)]
					answer = EventAnswer.objects.create(question=question, order=order, value=value)

				for cart_item in cart_items:
					for x in range(cart_item.quantity):

						name = form.cleaned_data['%s_%s_name' % (x, cart_item.id)]
						gender = form.cleaned_data['%s_%s_gender' % (x, cart_item.id)]
						if attendee_general_questions.email:
							email = form.cleaned_data['%s_%s_email' % (x, cart_item.id)]
						else:
							email = None
						attendee = Attendee.objects.create(ticket=cart_item.ticket, name=name, gender=gender, order=order, email=email)
						attendee.create_slug()
						attendee.save()

						for question in ticket_questions:
							try:
								value = form.cleaned_data['%s_%s_%s_ticketquestion' % (question.id, x, cart_item.id)]
								answer = TicketAnswer.objects.create(question=question, attendee=attendee, value=value)
							except:
								pass
							

				cart.processed = True
				cart.update_tickets_available()
				cart.save()
				del request.session['cart']
				request.session.modified = True
				messages.success(request, 'Congratulations, order complete!')


			except Exception as e:

				print(e)
				order.failed = True
				order.code_fail_reason = "Order Failed Due to Exception: %s" % (e)
				order.save()
				messages.warning(request, 'There was an error in proccessing your payment card. Please try again with a different payment card.')


		else:
			cart.processed = False
			cart.save()
			del request.session['cart']
			request.session.modified = True
			raise Http404

		valid_data = super(EventCheckoutView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, request, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, request=request, event=event))








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
		context["request"] = request
		return render(request, self.template_name, context)


class PastEventsView(HouseAccountMixin, EventMixin, ListView):
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
		context["inactive_event_tab"] = True
		return context




class EventCheckinCreateView(HouseAccountMixin, CreateView):
	model = Checkin
	form_class = CheckinForm
	template_name = "events/checkin/checkin_create.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_orders(self, event):
		orders = EventOrder.objects.filter(event=event, failed=False, payout=None).order_by('created_at')
		return orders

	def get_attendees(self, orders):
		attendees = Attendee.objects.filter(order__in=orders)
		return orders

	def get_context_data(self, form, event, request, *args, **kwargs):
		context = {}
		orders = self.get_orders(event)
		attendees = self.get_attendees(orders)
		context["event"] = event
		context["form"] = form
		context["attendees"] = attendees

		return context

	def get(self, request, *args, **kwargs):
		context = {}
		slug = kwargs['slug']
		event = self.get_event(slug)
		orders = self.get_orders(event)
		attendees = self.get_attendees(orders)
		form = CheckinForm(attendees=attendees)
		return self.render_to_response(self.get_context_data(form=form, event=event, request=request))


	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		event = self.get_event(slug)
		orders = self.get_orders(event) 

		form = EventPayoutForm(orders=orders, data=data)
		
		if form.is_valid():
			messages.success(request, 'Payout Sent!')
			return self.form_valid(form, orders, request, event)
		else:
			messages.warning(request, 'Oops! Something went wrong.')
			return self.form_invalid(form, request, event)


	def form_valid(self, form, orders, request, event):

		event_payout = EventPayout.objects.create(event=event)
		event_payout.save()
		amount = decimal.Decimal(0.00)

		for order in orders:
			order_value = form.cleaned_data['%s_order' % (order.id)]
			if order_value == True:
				try:
					order.payout = event_payout
					amount = amount + order.amount
					order.save()
				except:
					pass
			else:
				pass

		event_payout.amount = amount
		event_payout.save()

		valid_data = super(EventPayoutView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, request, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, request=request, event=event))





class EventCreateView(HouseAccountMixin, CreateView):
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



class EventUpdateView(HouseAccountMixin, UpdateView):
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
		context["dashboard_events"] = self.get_events()
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

		if "Archive Event" in data:
			self.object.active = False
			self.object.save()

		if "Re-Open Event" in data:
			self.object.active = True
			self.object.save()

		if "Delete Event" in data:
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





