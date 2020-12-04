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

from .models import Order, LineOrder
from .forms import MessageToRecipient
from profiles.models import Profile, Address


# Create your views here.

class LineOrderEdit(LoginRequiredMixin, FormView):

    template_name = "orders/edit.html"

    def get_success_url(self):

        profile = self.get_profile()
        order = self.get_order(profile)

        view_name = "profiles:orders:detail"
        return reverse(view_name, kwargs={"id": order.id})

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

    def get_line_order(self, order):
        try:
            line_order = LineOrder.objects.get(order=order, id=self.kwargs["line_order_id"])
            return line_order
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        form = MessageToRecipient()
        return render(request, self.template_name, self.get_context_data(form=form))


    def get_context_data(self, form, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        order = self.get_order(profile)
        line_order = self.get_line_order(order)
        sender_addresses = Address.objects.filter(profile=profile)
        context["sender_addresses"] = sender_addresses
        context["line_order"] = line_order
        context["order"] = order
        context["profile"] = profile
        return context


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        form = MessageToRecipient(data=data)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)


    def form_valid(self, form, request):
        # Post data
        data = request.POST
        message_to_recipient = form.cleaned_data.get('message_to_recipient')

        profile = self.get_profile()
        order = self.get_order(profile)
        line_order = self.get_line_order(order)
        line_order.message_to_recipient = message_to_recipient
        line_order.save()

        messages.success(request, 'Line Order Updated!')

        valid_data = super(LineOrderEdit, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



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







class OrderPublicDetail(View):

    template_name = "orders/public_detail.html"

    def get_profile(self, order):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            if order.profile == profile:
                return profile

            else:
                raise Http404
        except Exception as e:
            print(e)
            raise Http404

    def check_if_profile_is_active(self, order):
        if order.profile.temp_password:
            return False
        else:
            return True

    def get_order(self):
        try:
            order = Order.objects.get(public_id=self.kwargs["public_id"])
            return order
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        order = self.get_order()

        if request.user.is_authenticated:
            profile = self.get_profile(order)
            context["profile"] = profile

        if self.check_if_profile_is_active(order):
            context["active"] = True
        
        context["order"] = order
        return render(request, self.template_name, context)
