from __future__ import absolute_import, unicode_literals
from celery import shared_task

from events.models import Event
# Sending mail 
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils import timezone
from datetime import timedelta

from django.core.mail import send_mail, EmailMultiAlternatives
from events.forms import EventEmailConfirmationForm
from weasyprint import HTML, CSS

@shared_task
def archive_past_events(event_id):
	current_time = timezone.now()
	event = Event.objects.get(id=event_id)
	current_time = timezone.now()
	print("event name: %s" % (event.title))
	
	end_time_plus_1_day = event.end + timedelta(hours=24)
	if current_time >= end_time_plus_1_day:
		event.active = False
		event.save()
	else:
		print("not greater than time")


@shared_task
def send_test_email(event, message, email):
	event = Event.objects.get(id=event)
	subject = 'Order Confirmation For %s' % (event.title)
	context = {}
	context["event"] = event
	context["message"] = message
	html_message = render_to_string('emails/order_confirmation.html', context)
	plain_message = strip_tags(html_message)
	from_email = 'Arqam House Order Confirmation <info@arqamhouse.com>'
	print(email)
	to = ['%s' % (email)]
	send_mail(subject, plain_message, from_email, to,
				html_message=html_message, fail_silently=True)
	return "Done"
