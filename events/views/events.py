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
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from weasyprint import HTML, CSS
from django.utils.html import strip_tags

from django.core.validators import validate_email

from houses.mixins import HouseAccountMixin
from houses.models import HouseUser
from questions.models import Question
from events.mixins import EventMixin
from events.models import (Event, AttendeeCommonQuestions, EventQuestion, Ticket, EventCart, 
								EventCartItem, Answer, OrderAnswer, EventOrder, Attendee, EventEmailConfirmation)
from events.forms import EventForm, EventCheckoutForm
from payments.models import Transaction



# Create your views here.



class EventDashboardView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, DetailView):
	model = Event
	template_name = "events/event_dashboard.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_tickets(self, event):
		tickets = Ticket.objects.filter(event=event, deleted=False)
		return tickets

	def get_total_sales(self, event):
		orders = EventOrder.objects.filter(event=event, refunded=False, failed=False).select_related("transaction")
		total_sales = decimal.Decimal(0.00)
		for order in orders:
			if order.transaction.amount:
				total_sales += order.transaction.amount
		return total_sales


	def graph_data(self, event):
		
		today = timezone.now()
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
		questions = EventQuestion.objects.filter(event=event, question__deleted=False, question__approved=True)
		email = EventEmailConfirmation.objects.get(event=event)

		if event.active == False:
			context["inactive_event_tab"] = True
			context["event_tab"] = False
		else:
			context["event_tab"] = True

		context["email"] = email
		context["questions"] = questions
		context["tickets"] = tickets
		context["total_sales"] = self.get_total_sales(event)
		context["graph_data"] = self.graph_data(event)

		context["dashboard_events"] = dashboard_events
		context["house"] = house
		context["event"] = event
		context["request"] = request
		return render(request, self.template_name, context)



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



	def get_context_data(self, data=None, errors=None, *args, **kwargs):
		context = {}
		request = self.request
		slug = self.kwargs['slug']
		event = self.get_event(slug)
		cart = self.get_cart()
		cart_items = EventCartItem.objects.filter(event_cart=cart)
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
			
		context["errors"] = errors
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
		if not cart_items.exists():
			return HttpResponseRedirect(self.get_success_url())

		return render(request, self.template_name, self.get_context_data())


	def validate_data(self, data, event, cart):
		errors = {}

		# Check buyer name and email
		print(data["name"])
		if data["name"] == "":
			errors["name"] = "Please enter the buyers full name."

		if data["email"] == "":
			errors["email"] = "Please enter your email address. Watch for typos, your tickets get sent there!"
		else:
			try:
				validate_email(data["email"])
			except:
				errors["email"] = "Invalid email address, please enter a valid email address so we can send your ticket there!"


		order_questions = EventQuestion.objects.filter(event=event, order_question=True, question__deleted=False, question__approved=True).order_by("question__order")
		for order_question in order_questions:
			value = data["%s_order_question" % (order_question.question.id)]

			if order_question.question.required and value == "":
				if order_question.question.question_type == "Simple" or order_question.question.question_type == "Long":
					errors["%s_order_question" % (
						order_question.question.id)] = "Please enter a valid answer for question '%s'." % (order_question.question.title)

		cart_items = EventCartItem.objects.filter(event_cart=cart)
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)

		for cart_item in cart_items:
			if not cart_item.ticket.express:
				for quantity in range(cart_item.quantity):
					attendee_name = data["%s_%s_name" % (quantity, cart_item.ticket.id)]
					
					if attendee_name == "":
						errors["%s_%s_name" % (quantity, cart_item.ticket.id)] = "Please enter the attendees full name."

					if attendee_common_questions.age:
						attendee_age = data["%s_%s_age" % (quantity, cart_item.ticket.id)]

						if attendee_common_questions.age_required:
							if attendee_age == "":
								errors["%s_%s_age" % (quantity, cart_item.ticket.id)] = "Please enter the attendees age."

					if attendee_common_questions.address:
						try:
							attendee_address = data["%s_%s_address" % (quantity, cart_item.ticket.id)]
							if attendee_common_questions.address_required:
								if attendee_address == "":
									errors["%s_%s_address" % (quantity, cart_item.ticket.id)] = "Please enter the attendees address."
						except:
							pass

					attendee_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id, question__deleted=False, question__approved=True).order_by("question__order")
					for attendee_question in attendee_questions:
						value = data["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)]

						if attendee_question.question.required and value == "":
							if attendee_question.question.question_type == "Simple" or attendee_question.question.question_type == "Long":
								errors["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)] = "Please enter a valid answer for question '%s'." % (attendee_question.question.title)


		return errors



	def post(self, request, *args, **kwargs):
		data = request.POST

		print("\n\nerrors")
		print(data)
		print("errors\n\n")

		errors = {}
		slug = kwargs['slug']
		event = self.get_event(slug)
		cart = self.get_cart()

		errors = self.validate_data(data, event, cart)
		print("\n\nerrors")
		print(errors)
		print("errors\n\n")

		if errors:
			return self.render_to_response(self.get_context_data(data=data, errors=errors))

		# Only get the Stripe Token if payment enabled
		if cart.pay:
			stripe_token = data["stripeToken"]

		# Get buyer name and email address
		name = data['name']
		email = data['email']

		# Create Transaction Object
		transaction = Transaction.objects.create(house=event.house, name=name)
		transaction.save()

		# Create Order Object
		order = EventOrder.objects.create(name=name, email=email, event=event, event_cart=cart, transaction=transaction, house_created=cart.house_created)
		order.save()

		# Get Buyer questions and make answers
		order_questions = EventQuestion.objects.filter(event=event, order_question=True, question__deleted=False, question__approved=True).order_by("question__order")
		for order_question in order_questions:
			value = data["%s_order_question" % (order_question.question.id)]

			# Create Order answers
			order_answer = OrderAnswer.objects.create(question=order_question, value=value, order=order)
			order_answer.save()

		# get answers from attendees 
		cart_items = EventCartItem.objects.filter(event_cart=cart)
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
		

		for cart_item in cart_items:

			if cart_item.ticket.express:
				for quantity in range(cart_item.quantity):

					attendee_name = "%s-%s" % (order.name, int(quantity)+1)
					if cart_item.donation_ticket:
						attendee = Attendee.objects.create(
							order=order, ticket=cart_item.ticket, name=attendee_name, email=email, gender=None,
							ticket_buyer_price=cart_item.donation_buyer_amount, ticket_price=cart_item.donation_amount, ticket_fee=cart_item.donation_fee,
							ticket_pass_fee=True)
					else:
						attendee = Attendee.objects.create(
							order=order, ticket=cart_item.ticket, name=attendee_name, email=email, gender=None,
							ticket_buyer_price=cart_item.ticket_buyer_price, ticket_price=cart_item.ticket_price, ticket_fee=cart_item.ticket_fee,
							ticket_pass_fee=cart_item.pass_fee)
					attendee.save()

			else:
				attendee_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id, question__deleted=False, question__approved=True).order_by("question__order")
				for quantity in range(cart_item.quantity):

					attendee_email = None
					age = None
					gender = None
					address = None
					
					# Step 3a get the attendee_name
					attendee_name = data["%s_%s_name" % (quantity, cart_item.ticket.id)]

					# Step 3b answers to common questions
					if attendee_common_questions.email:
						attendee_email = data["%s_%s_email" % (quantity, cart_item.ticket.id)]

					if attendee_common_questions.age:
						age = data["%s_%s_age" % (quantity, cart_item.ticket.id)]

					if attendee_common_questions.gender:
						gender = data["%s_%s_gender" % (quantity, cart_item.ticket.id)] 

					if attendee_common_questions.address:
						try:
							address = data["%s_%s_address" % (quantity, cart_item.ticket.id)]
						except:
							address = "N/A"

					if cart_item.donation_ticket:
						attendee = Attendee.objects.create(
							order=order, ticket=cart_item.ticket, name=attendee_name, email=attendee_email, age=age, gender=gender, address=address,
							ticket_buyer_price=cart_item.donation_buyer_amount, ticket_price=cart_item.donation_amount, ticket_fee=cart_item.donation_fee,
							ticket_pass_fee=True)
					else:
						attendee = Attendee.objects.create(
							order=order, ticket=cart_item.ticket, name=attendee_name, email=attendee_email, age=age, gender=gender, address=address,
							ticket_buyer_price=cart_item.ticket_buyer_price, ticket_price=cart_item.ticket_price, ticket_fee=cart_item.ticket_fee,
							ticket_pass_fee=cart_item.pass_fee)
					attendee.save()

					# Step 3c answers to custom questions
					for attendee_question in attendee_questions:
						value = data["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)]

						answer = Answer.objects.create(question=attendee_question, value=value, attendee=attendee)
						answer.save()


		# If there is a payment to be made
		if cart.pay:
			stripe.api_key = settings.STRIPE_SECRET_KEY
			
			try:
				charge = stripe.Charge.create(
							amount = int(cart.total * 100),
							currency = 'cad',
							description = self.get_charge_description(event, order),
							source = stripe_token,
							metadata = {
                                    	'transaction_amount': cart.total,
										'transaction_arqam_amount': cart.arqam_charge,
										'transaction_stripe_amount': cart.stripe_charge,
										'transaction_house_amount': cart.total_no_fee,
										'buyer_email': data['email'],
										'buyer_name': data['name'],
										'order_id': order.public_id,
										'event_name': order.event.title,
										'event_id': order.event.pk,
										'house_name': order.event.house.name,
										'house_id': order.event.house.pk
										},
                                    statement_descriptor=self.get_charge_descriptor(event),
						)

				print("Charge goes here")
				print(charge)
				print("Charge goes here")

				transaction.amount = cart.total
				transaction.arqam_amount = cart.arqam_charge
				transaction.stripe_amount = cart.stripe_charge
				transaction.house_amount = cart.total_no_fee

				transaction.payment_id = charge['id']
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

				print("Cart Processed")
				print(cart.processed)

				self.send_confirmation_email(event, data['email'], order)
				self.send_owner_confirmation_email(event, order)
				messages.success(request, 'Check your email for tickets and further instructions.')
				return HttpResponseRedirect(self.get_success_url())

			except stripe.error.CardError as e:
				print(e)

				transaction.payment_id = e.error.charge
				transaction.failure_code = e.error.code
				transaction.failure_message = e.error.message
				transaction.outcome_type = e.error.type
				transaction.network_status = e.http_status
				transaction.reason = e.error.param
				transaction.email = order.email

				order.failed = True
				transaction.failed = True
				transaction.code_fail_reason = e.error.message
				order.save()
				transaction.save()
				cart.processed = False
				cart.save()
				del request.session['cart']
				request.session.modified = True
				messages.error(request, "%s Please try again." % (e.error.message))
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


		else:

			transaction.amount = 0.00
			transaction.arqam_amount = 0.00
			transaction.stripe_amount = 0.00
			transaction.house_amount = 0.00

			transaction.email = data['email']

			cart.processed = True
			cart.update_tickets_available()
			cart.save()
			del request.session['cart']
			request.session.modified = True
			self.send_confirmation_email(event, data['email'], order)
			messages.success(request, 'Check your email for tickets and further instructions.')
			return HttpResponseRedirect(self.get_success_url())


		return render(request, self.template_name, self.get_context_data(data))

	def send_confirmation_email(self, event, email, order):

		# PDF Attachment
		pdf_context = {}
		pdf_context["order"] = order
		pdf_content = render_to_string('pdfs/ticket.html', pdf_context)
		pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))
		pdf_file = HTML(string=pdf_content).write_pdf(stylesheets=[pdf_css])

		# Compose Email
		subject = 'Order Confirmation For %s' % (event.title)
		email_confirmation = EventEmailConfirmation.objects.get(event=event)
		context = {}
		context["event"] = event
		context["message"] = email_confirmation.message
		html_content = render_to_string('emails/order_confirmation.html', context)
		text_content = strip_tags(html_content)
		from_email = 'Order Confirmation <info@arqamhouse.com>'
		to = ['%s' % (email)]
		email = EmailMultiAlternatives(subject=subject, body=text_content,
		                               from_email=from_email, to=to)
		email.attach_alternative(html_content, "text/html")
		email.attach("confirmation.pdf", pdf_file, 'application/pdf')
		email.send()
		return "Done"

	def send_owner_confirmation_email(self, event, order):

		house_users = HouseUser.objects.filter(house=event.house)
		to_emails = []
		for house_user in house_users:
			to_emails.append(house_user.profile.email)
		# Compose Email
		subject = 'New Order For %s' % (event.title)
		context = {}
		context["event"] = event
		context["order"] = order
		html_content = render_to_string('emails/owner_order_confirmation.html', context)
		text_content = strip_tags(html_content)
		from_email = 'New Order <info@arqamhouse.com>'
		to = to_emails
		email = EmailMultiAlternatives(subject=subject, body=text_content,
		                               from_email=from_email, to=to)
		email.attach_alternative(html_content, "text/html")
		email.send()
		return "Done"

	def get_charge_description(self, event, order):
		return ("Order #: %s for Event: %s (Event ID: %s)." % (order.id, event.title, event.id))


	def get_charge_descriptor(self, event):
		event_title = "AH* %s" % (event.title)
		if len(event_title) > 20:
			descriptor = "AH* %s" % (event.house.name)
			if len(descriptor) > 20:
				descriptor = 'Arqam House Inc.'
		else:
			descriptor = event_title
		return descriptor




class PastEventsView(HouseAccountMixin, UserPassesTestMixin, EventMixin, ListView):
	model = Event
	template_name = "events/past_events.html"

	def test_func(self):
		house_users = HouseUser.objects.filter(profile=self.request.user)
		house = self.get_house()
		for house_user in house_users:
			if house == house_user.house:
				return True
		return False


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



class EventCreateView(HouseAccountMixin, CreateView):
	model = Event
	form_class = EventForm
	template_name = "events/event_form.html"

	def get_success_url(self):
		event = self.object
		view_name = "events:landing"
		return reverse(view_name, kwargs={'slug': event.slug})

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

		messages.success(request, 'Your event is live! Click <a href="%s">here</a> to add tickets' %
		                 (reverse('events:list_tickets', kwargs={'slug': self.object.slug})))
		valid_data = super(EventCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



class EventUpdateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):
	model = Event
	form_class = EventForm
	template_name = "events/event_form.html"

	def get_success_url(self):
		view_name = "events:landing"
		return reverse(view_name, kwargs={"slug": self.object.slug})

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
		context["time"] = timezone.now()
		
		if self.object.active == False:
			context["inactive_event_tab"] = True
			context["events_tab"] = False
		else:
			context["events_tab"] = True

		context["update_event"] = True

		if self.object.active:
			context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):
		slug = kwargs['slug']
		self.object = self.get_event(slug)

		data = request.GET

		if 'url' in data:

			url = data['url']
			slugify_url = slugify(url)
			
			if Event.objects.filter(slug=slugify_url).exists():
				return HttpResponse("taken")
			else:
				return HttpResponse("not_taken")
		else:
			initial = {}
			if self.object.start:
				initial["start"] = self.object.start.strftime("%m/%d/%Y %I:%M %p")
			if self.object.end:
				initial["end"] = self.object.end.strftime("%m/%d/%Y %I:%M %p")
			form = EventForm(instance=self.object, initial=initial)
			
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

		elif "Remove" in data:
			self.object.image = None
			self.object.save()
			messages.warning(request, 'Event Image Removed')

		elif "Re-Open" in data:
			self.object.active = True
			self.object.save()
			messages.info(request, 'Event Re-Opened')

		elif "Delete" in data:
			self.object.active = False
			self.object.deleted = True
			self.object.save()
			messages.warning(request, 'Event Deleted Successfully')
			return HttpResponseRedirect(self.get_success_delete_url())

		else:
			messages.success(request, 'Event Updated Successfully!')
			
		valid_data = super(EventUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))





