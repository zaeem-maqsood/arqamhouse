from __future__ import absolute_import, unicode_literals
from celery import shared_task

from subscribers.models import Subscriber, Campaign
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
def send_campaign_emails(campaign_id):

    print("We came to send emails")
    to = []
    campaign = Campaign.objects.get(id=campaign_id)
    subscribers = Subscriber.objects.filter(house=campaign.house)
    for subscriber in subscribers:
        to = [subscriber.profile.email]
        print(to)
        # Compose Email
        subject = f"{campaign.subject}"
        context = {}
        context["campaign"] = campaign
        campaign_content = campaign.content.replace('[name]', subscriber.profile.name)
        context["campaign_content"] = campaign_content
        context["house"] = campaign.house
        context["subscriber"] = subscriber
        html_content = render_to_string('emails/campaign_email.html', context)
        text_content = strip_tags(html_content)

        from_email = f"{campaign.house.name} <{campaign.house.email}>"
        email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()
    return "Done"
