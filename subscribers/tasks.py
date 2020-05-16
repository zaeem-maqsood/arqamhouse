from __future__ import absolute_import, unicode_literals
from celery import shared_task


from houses.models import House
from subscribers.models import Subscriber, Campaign
from donations.models import Donation
# Sending mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Sum, Avg

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
    subscribers = campaign.subscribers_sent_to.all()
    
    for subscriber in subscribers:
        to = [str(subscriber.profile.email)]
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

        if campaign.house.email:
            from_email = f"{campaign.house.name} <{campaign.house.email}>"
        else:
            from_email = f"{campaign.house.name} <info@arqamhouse.com>"

        email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()
    return "Done"



# In donation models
@shared_task
def update_all_subscribers_who_have_donated(house_id):

    house = House.objects.get(id=house_id)
    subscribers = Subscriber.objects.filter(house=house)

     # Aggregate the avg amount of times people have donated
    time_donated_average = subscribers.aggregate(Avg('times_donated'))["times_donated__avg"]
    house.donation_score = time_donated_average

    # Aggregate the avg amount people have donated
    donations = Donation.objects.filter(donation_type__house=house)
    average_donation_amount = donations.aggregate(Avg('transaction__amount'))["transaction__amount__avg"]
    house.donation_amount_score = average_donation_amount

    house.save()

    for subscriber in subscribers:
        if subscriber.amount_donated:
            subscriber.save()
    
    return "Done"
