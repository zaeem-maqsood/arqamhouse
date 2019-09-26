from .base import *

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from events.models import EventEmailConfirmation, EventOrder
from django.core.mail import send_mail, EmailMultiAlternatives
from events.forms import EventEmailConfirmationForm
from weasyprint import HTML, CSS


class EventConfirmationEmailView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):
	model = EventEmailConfirmation
	form_class = EventEmailConfirmationForm
	template_name = "events/emails/confirmation_email.html"

	def get_success_url(self):
		view_name = "events:email_confirmation"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_context_data(self, *args, **kwargs):
		context = {}
		slug = self.kwargs['slug']
		event = self.get_event(slug)
		house = self.get_house()

		context["form"] = self.get_form()
		context["house"] = house
		context["event"] = event

		context["update_event"] = True
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):
		slug = kwargs['slug']
		event = self.get_event(slug)

		# Get Email confirmation object
		self.object = EventEmailConfirmation.objects.get(event=event)

		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		slug = kwargs['slug']
		event = self.get_event(slug)

		# Get Email confirmation object
		self.object = EventEmailConfirmation.objects.get(event=event)

		data = request.POST


		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, event)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request, event):
		data = request.POST
		self.object = form.save()

		if 'send-test' in data:
			self.send_test_email(event)
			messages.success(request, 'Test email sent to %s' % (request.user.email))
		else:
			messages.success(request, 'Confirmation Email Updated')
		valid_data = super(EventConfirmationEmailView, self).form_valid(form)
		return valid_data


	def send_test_email(self, event):
		subject = 'Order Confirmation For %s' % (event.title)
		context = {}
		context["event"] = event
		context["message"] = self.object.message
		html_message = render_to_string('emails/order_confirmation.html', context)
		plain_message = strip_tags(html_message)
		from_email = 'Arqam House Order Confirmation <info@arqamhouse.com>'
		print(self.request.user.email)
		to = ['%s' % (self.request.user.email)]
		send_mail(subject, plain_message, from_email, to, html_message=html_message, fail_silently=True)
		return "Done"

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))
