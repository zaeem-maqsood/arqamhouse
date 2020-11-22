from django.utils import timezone
from django.utils.timezone import datetime, timedelta
from django.conf import settings
from django.db.models import Q
from django.core import serializers
from django.template.loader import render_to_string
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views import View
from django.urls import reverse
from django.contrib import messages

from core.mixins import LoginRequiredMixin

from .models import Order
from profiles.models import Profile


# Create your views here.

class OrderList(LoginRequiredMixin, View):

    template_name = "orders/list.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        orders = Order.objects.filter(profile=profile).order_by("-created_at")
        context["orders"] = orders
        context["profile"] = profile
        print(profile.name)
        return render(request, self.template_name, context)






class OrderDetail(LoginRequiredMixin, View):

    template_name = "orders/detail.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except Exception as e:
            print(e)
            raise Http404

    def get_order(self, profile):
        try:
            order = Order.objects.get(profile=profile, id=self.kwargs["id"])
            return order
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        order = self.get_order(profile)
        context["order"] = order
        context["profile"] = profile
        print(profile.name)
        return render(request, self.template_name, context)



