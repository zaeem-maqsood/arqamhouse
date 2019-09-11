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

from houses.mixins import HouseAccountMixin
from events.models import Event