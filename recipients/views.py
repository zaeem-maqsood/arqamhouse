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

from django.shortcuts import render
from .models import Recipient
from .forms import RecipientForm

from profiles.models import Address, Profile

# Create your views here.


class RecipientList(LoginRequiredMixin, View):

    template_name = "recipients/list.html"

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
        recipients = Recipient.objects.filter(profile=profile, deleted=False)
        context["recipients"] = recipients
        context["profile"] = profile
        print(profile.name)
        return render(request, self.template_name, context)


class AddRecipient(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "recipients/add_recipient.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "profiles:recipients:list"
        return reverse(view_name)

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        context["form"] = form
        context["profile"] = profile
        return context

    def form_valid(self, form, request):
        data = request.POST
        profile = self.get_profile()
        form.instance.profile = profile
        self.object = form.save()
        messages.success(request, "Recipient Created")
        valid_data = super(AddRecipient, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class UpdateRecipient(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "recipients/update_recipient.html"

    def get_recipient(self, profile):
        try:
            recipient = Recipient.objects.get(profile=profile, id=self.kwargs["id"])
            return recipient
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        self.object = self.get_recipient(profile)
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "profiles:recipients:list"
        return reverse(view_name)

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            raise Http404

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        self.object = self.get_recipient(profile)
        data = request.POST
        print(data)

        if 'delete' in data:
            print("Is it coming here")
            recipient = self.get_recipient(profile)
            recipient.deleted = True
            recipient.save()
            messages.warning(request, 'Recipient Deleted')
            return HttpResponseRedirect(self.get_success_url())

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        context["form"] = form
        context["profile"] = profile
        context["recipient"] = self.object
        return context

    def form_valid(self, form, request):
        data = request.POST
        profile = self.get_profile()
        messages.success(request, "Recipient Updated")
        self.object = form.save()

        valid_data = super(UpdateRecipient, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
