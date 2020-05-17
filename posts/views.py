import json
from django.db.models import Q
from django.core import serializers
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views import View
from django.urls import reverse
from django.conf import settings

from django.core.mail import send_mail, EmailMultiAlternatives

from weasyprint import HTML, CSS
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from itertools import chain
from operator import attrgetter

from houses.mixins import HouseAccountMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from events.mixins import EventSecurityMixin
from django.contrib import messages

from subscribers.models import Subscriber, Campaign, Audience
from subscribers.forms import AddSubscriberForm

from donations.models import Donation
from houses.models import House
from profiles.models import Profile
from django.contrib.auth.models import User
from events.models import EventOrder, Attendee, Event, Ticket, EventCart, EventCartItem

import boto3
from botocore.client import Config



# Create your views here.
class EditPostView(HouseAccountMixin, FormView):
    template_name = "posts/edit_post.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data(request=request))

    def get_context_data(self, request, *args, **kwargs):
        context = {}
        froala_key = settings.FROALA_EDITOR_OPTIONS["key"]

        s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        print(s3_client)
        context["froala_key"] = froala_key
        return context

