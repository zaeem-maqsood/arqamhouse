from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from django.contrib.auth.mixins import UserPassesTestMixin
from events.mixins import EventSecurityMixin

from houses.mixins import HouseAccountMixin
from events.models import Event




from django.utils.safestring import mark_safe
import json


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
