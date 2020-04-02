import json
import stripe
import decimal

from django.conf import settings
from django.shortcuts import render, get_object_or_404

from django.views import View
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView

from django.utils import timezone
from django.utils.timezone import datetime, timedelta, get_current_timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email

from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin


from django.db.models import Q
from django.db.models import Sum
from django.template.loader import render_to_string

from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from twilio.rest import Client
from weasyprint import HTML, CSS
from opentok import OpenTok

# Mixins
from events.mixins import EventSecurityMixin, EventMixin
from houses.mixins import HouseAccountMixin

# Tasks
from events.tasks import send_test_email
from subscribers.tasks import send_campaign_emails

# Models
from houses.models import HouseUser, House
from events.models import (Event, AttendeeCommonQuestions, EventQuestion, Ticket, EventCart, ChargeError,
                           EventCartItem, Answer, OrderAnswer, EventOrder, Attendee, EventEmailConfirmation,
                           EventRefundRequest, EventDiscount, Checkin, EventOrderRefund, EventRefererDomain, 
                           EventLive)
from questions.models import Question
from payments.models import Transaction, Refund, HouseBalance
from profiles.models import Profile
from subscribers.models import Subscriber, Campaign

# Forms
from events.forms import (EventForm, EventCheckoutForm, AttendeeForm, TicketsToCartForm, CheckinForm, DiscountForm,
                          EventEmailConfirmationForm, FreeTicketForm, PaidTicketForm, DonationTicketForm, EventMainForm,
                          EventVenueForm, EventImageForm, EventDescriptionForm, EventURLForm)




def archive_past_events(event):
    if event.active and event.end:
        current_time = timezone.now()
        end_time_plus_1_day = event.end + timedelta(hours=24)
        if current_time >= end_time_plus_1_day:
            event.active = False
            event.save()
    return "done"



class OpenTokSubscriberView(View):

    template_name = "events/opentok/subscriber.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        api_key = settings.OPEN_TOK_API_KEY
        api_secret = settings.OPEN_TOK_SECRECT_KEY
        print(api_key)
        print(api_secret)
        opentok = OpenTok(api_key, api_secret)
        # session = opentok.create_session()
        # session_id = session.session_id
        # token = session.generate_token()
        # print(token)
        # print(session_id)

        api_key = 46593362
        session_id = '1_MX40NjU5MzM2Mn5-MTU4NDk3NjU2NDc2Nn54K3RDWFVMNGlvRGg0TU13VmpQNkZKWUN-UH4'
        # token = 'T1==cGFydG5lcl9pZD00NjU5MzM2MiZzaWc9ZmU2OTRiYmQzMWIzNmJhNzRlOTZkYjlmOWNjZWMxMDkyMjRkMmI2NTpzZXNzaW9uX2lkPTFfTVg0ME5qVTVNek0yTW41LU1UVTRORGszTmpVMk5EYzJObjU0SzNSRFdGVk1OR2x2UkdnMFRVMTNWbXBRTmtaS1dVTi1VSDQmY3JlYXRlX3RpbWU9MTU4NDk3NjU2NCZleHBpcmVfdGltZT0xNTg1MDYyOTY0JnJvbGU9cHVibGlzaGVyJm5vbmNlPTUyMDA3NyZpbml0aWFsX2xheW91dF9jbGFzc19saXN0PQ=='
        token = opentok.generate_token(session_id)

        context["api_key"] = api_key
        context["session_id"] = session_id
        context["token"] = token
        return context


class OpenTokPublisherView(View):

    template_name = "events/opentok/publisher.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        api_key = settings.OPEN_TOK_API_KEY
        api_secret = settings.OPEN_TOK_SECRECT_KEY
        print(api_key)
        print(api_secret)
        opentok = OpenTok(api_key, api_secret)
        # session = opentok.create_session()
        # session_id = session.session_id
        # token = session.generate_token()
        # print(token)
        # print(session_id)


        api_key = 46593362
        session_id = '1_MX40NjU5MzM2Mn5-MTU4NDk3NjU2NDc2Nn54K3RDWFVMNGlvRGg0TU13VmpQNkZKWUN-UH4'
        # token = 'T1==cGFydG5lcl9pZD00NjU5MzM2MiZzaWc9ZmU2OTRiYmQzMWIzNmJhNzRlOTZkYjlmOWNjZWMxMDkyMjRkMmI2NTpzZXNzaW9uX2lkPTFfTVg0ME5qVTVNek0yTW41LU1UVTRORGszTmpVMk5EYzJObjU0SzNSRFdGVk1OR2x2UkdnMFRVMTNWbXBRTmtaS1dVTi1VSDQmY3JlYXRlX3RpbWU9MTU4NDk3NjU2NCZleHBpcmVfdGltZT0xNTg1MDYyOTY0JnJvbGU9cHVibGlzaGVyJm5vbmNlPTUyMDA3NyZpbml0aWFsX2xheW91dF9jbGFzc19saXN0PQ=='
        token = opentok.generate_token(session_id)

        # To get all streams in a session:
        stream_list = opentok.list_streams(session_id)
        print(stream_list)
        stream = stream_list.items
        print(len(stream))

        if len(stream) == 0:
            allow_publish = True
        else:
            allow_publish = False

        context["allow_publish"] = allow_publish

        context["api_key"] = api_key
        context["session_id"] = session_id
        context["token"] = token
        return context



class ChannelsView(View):

    template_name = "events/channels/testing.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *args, **kwargs):
        context = {}
        return context


class ChannelsRoomView(View):

    template_name = "events/channels/room.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}

        local = settings.DEBUG
        context["local"] = local
        room_name = self.kwargs["room_name"]
        print(room_name)

        context["room_name_json"] = mark_safe(json.dumps(room_name))
        return context



CONTENT = """
            <p style="text-align: center;">
                <span style="font-size: 24px; font-weight:100; color:  grey;">[house_name] has a new event coming up!</span>
            </p>
            <p style="user-select: auto; text-align: center;">
                <br style="user-select: auto;">
            </p>
            <p style="user-select: auto; text-align: center;">
                <span style="font-size: 18px; user-select: auto; color: rgb(44, 130, 201);">[event_name]</span>
            </p>
            <p style="user-select: auto; text-align: center;">
                <span style="font-size: 24px; user-select: auto;">
                    <br style="user-select: auto;">
                    <img src="[event_image]" style="width: 193px; display: inline-block; vertical-align: bottom; margin-right: 5px; margin-left: 5px; text-align: center; user-select: auto; max-width: calc(100% - 10px);">&nbsp;
                </span>
            </p>
            <p style="user-select: auto; text-align: center;">
                <br style="user-select: auto;">
            </p>
            <p style="user-select: auto; text-align: center;">
                <a href="[event_url]" style="background-color: rgb(74, 144, 226); border: 0px solid rgb(74, 144, 226); border-radius: 6px; color: rgb(255, 255, 255); display: inline-block; font-size: 14px; font-weight: normal; letter-spacing: 0px; line-height: normal; padding: 12px 18px; text-align: center; text-decoration: none; width: 280px; user-select: auto;" target="_blank">View Event</a>
            </p>

            """


NO_IMAGE_CONTENT = """
            <p style="text-align: center;">
                <span style="font-size: 24px; font-weight:100; color:  grey;">[house_name] has a new event coming up!</span>
            </p>
            <p style="user-select: auto; text-align: center;">
                <br style="user-select: auto;">
            </p>
            <p style="user-select: auto; text-align: center;">
                <span style="font-size: 18px; user-select: auto; color: rgb(44, 130, 201);">[event_name]</span>
            </p>
            <p style="user-select: auto; text-align: center;">
                <br style="user-select: auto;">
            </p>
            <p style="user-select: auto; text-align: center;">
                <a href="[event_url]" style="background-color: rgb(74, 144, 226); border: 0px solid rgb(74, 144, 226); border-radius: 6px; color: rgb(255, 255, 255); display: inline-block; font-size: 14px; font-weight: normal; letter-spacing: 0px; line-height: normal; padding: 12px 18px; text-align: center; text-decoration: none; width: 280px; user-select: auto;" target="_blank">View Event</a>
            </p>

            """
