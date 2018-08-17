import stripe
import decimal
from django.conf import settings
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages

from organizations.mixins import OrganizationAccountMixin
from questions.models import EventQuestion, AllTicketQuestionControl, TicketQuestion
from answers.models import EventAnswer, TicketAnswer
from carts.models import EventCart, EventCartItem
from attendees.models import Attendee
from orders.models import EventOrder
from .mixins import EventMixin
from .models import Event, EventGeneralQuestions, AttendeeGeneralQuestions
from .forms import EventForm, EventCheckoutForm




# Create your views here.


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
			descriptor = event.organization.name
			if len(descriptor) > 20:
				descriptor = 'Arqam House Inc.'
		else:
			descriptor = event_title
		return descriptor

	def form_valid(self, form, request, event, cart, token):


		if token:
			# Create Order
			order = EventOrder.objects.create(event=event, event_cart=cart)

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

				# Save Event Questions
				for question in event_questions:
					value = form.cleaned_data['%s_eventquestion' % (question.id)]
					answer = EventAnswer.objects.create(question=question, order=order, value=value)

				for cart_item in cart_items:
					for x in range(cart_item.quantity):

						name = form.cleaned_data['%s_%s_name' % (x, cart_item.id)]
						gender = form.cleaned_data['%s_%s_gender' % (x, cart_item.id)]
						email = form.cleaned_data['%s_%s_email' % (x, cart_item.id)]
						attendee = Attendee.objects.create(ticket=cart_item.ticket, name=name, gender=gender, order=order)

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

	def get(self, request, *args, **kwargs):
		context = {}
		slug = kwargs['slug']
		try:
			event = Event.objects.get(slug=slug)
		except:
			raise Http404

		context["event"] = event
		context["request"] = request
		return render(request, self.template_name, context)


class ActiveEventsBackendListView(OrganizationAccountMixin, EventMixin, ListView):
	model = Event
	template_name = "events/active_backend_events.html"


	def get_context_data(self, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		active_events = self.get_active_events(organization)
		print(active_events)
		context["events"] = active_events
		context["organization"] = organization
		context["events_tab"] = True
		context["active_event_tab"] = True
		return context


class EventCreateView(OrganizationAccountMixin, CreateView):
	model = Event
	form_class = EventForm
	template_name = "events/event_create.html"

	def get_success_url(self):
		view_name = "dashboard"
		return reverse(view_name)

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		context["form"] = form
		context["organization"] = organization
		context["events_tab"] = True
		context["create_event_tab"] = True
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
		organization = self.get_organization()
		form.instance.organization = organization
		self.object = form.save()

		if "Create" in data:
			self.object.active = True
			self.object.save()
			messages.success(request, 'Event Published')
		valid_data = super(EventCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))





