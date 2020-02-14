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


from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from twilio.rest import Client
from weasyprint import HTML, CSS

# Mixins
from events.mixins import EventSecurityMixin, EventMixin
from houses.mixins import HouseAccountMixin

# Tasks
from events.tasks import send_test_email

# Models
from houses.models import HouseUser
from events.models import (Event, AttendeeCommonQuestions, EventQuestion, Ticket, EventCart, ChargeError,
                           EventCartItem, Answer, OrderAnswer, EventOrder, Attendee, EventEmailConfirmation,
                           EventRefundRequest, EventDiscount, Checkin, EventOrderRefund, )
from questions.models import Question
from payments.models import Transaction, Refund, HouseBalance
from profiles.models import Profile
from subscribers.models import Subscriber

# Forms
from events.forms import (EventForm, EventCheckoutForm, AttendeeForm, TicketsToCartForm, CheckinForm, DiscountForm,
                          EventEmailConfirmationForm, FreeTicketForm, PaidTicketForm, DonationTicketForm)







def archive_past_events(event):
    if event.active:
        current_time = timezone.now()
        end_time_plus_1_day = event.end + timedelta(hours=24)
        if current_time >= end_time_plus_1_day:
            event.active = False
            event.save()
    return "done"



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

        room_name = self.kwargs["room_name"]
        print(room_name)

        context["room_name_json"] = mark_safe(json.dumps(room_name))
        return context
