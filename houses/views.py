import stripe
import random
import decimal
import numpy as np
import sys
import time
import json
from base64 import b64encode
from PIL import Image
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile

from django.db.models import Sum
from django.utils.timezone import datetime, timedelta
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.template.loader import render_to_string

from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.core import mail
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email

from twilio.rest import Client

from .mixins import HouseAccountMixin, HouseLandingMixin

from core.mixins import LoginRequiredMixin

from itertools import chain
from operator import attrgetter

from django.contrib.auth.models import User
from profiles.models import Profile
from .models import House, HouseUser, HouseDirector
from .forms import (AddUserToHouse, HouseSupportInfoForm, HouseChangeForm, HouseForm, HouseVerificationForm, 
                    HouseDirectorForm, HouseUserOptionsForm, HouseLogoForm, HouseContactForm)

from events.models import Event, Ticket, EventCart, EventCartItem, EventOrder, Attendee, EventLiveArchive
from profiles.models import Profile
from payments.models import HouseBalance, HouseBalanceLog, Transaction, PayoutSetting
from subscribers.models import Subscriber
from donations.models import Donation, DonationType



class HouseEventsListView(View):
    template_name = "houses/events.html"

    def get_house(self, slug):
        try:
            house = House.objects.get(slug=slug)
            return house
        except:
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        house = self.get_house(kwargs["slug"])
        active_events = Event.objects.filter(house=house, deleted=False, active=True).order_by("-updated_at")
        past_events = Event.objects.filter(house=house, deleted=False, active=False).order_by("-updated_at")

        total_events = active_events.count() + past_events.count()
        tickets_sold = Ticket.objects.filter(event__house=house).aggregate(Sum('amount_sold'))["amount_sold__sum"]

        context["total_events"] = total_events
        context["tickets_sold"] = tickets_sold
        context["active_events"] = active_events
        context["past_events"] = past_events
        context["house"] = house
        return render(request, self.template_name, context)


class AllArchivedListView(View):
    template_name = "houses/archives.html"

    def get_house(self, slug):
        try:
            house = House.objects.get(slug=slug)
            return house
        except:
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        house = self.get_house(kwargs["slug"])
        event_live_archives = EventLiveArchive.objects.filter(event_live__event__house=house).order_by("created_at")
        context["event_live_archives"] = event_live_archives
        context["house"] = house
        return render(request, self.template_name, context)



class HouseHomePageView(DetailView):
    model = House
    template_name = "houses/house_home_page.html"

    def get_house(self, slug):
        try:
            house = House.objects.get(slug=slug)
            return house
        except:
            raise Http404 

    def check_if_user_is_owner(self, house):
        user = self.request.user
        if user.is_anonymous:
            return False
        house_users = HouseUser.objects.filter(profile=user, house=house)
        print(house_users)
        if house_users.exists():
            return True
        else:
            return False

    
    def check_if_user_is_subscribed(self, house):
        user = self.request.user 
        if user.is_authenticated:
            try:
                subscriber = Subscriber.objects.get(profile=user, house=house)
                if subscriber.unsubscribed:
                    return False
                else:
                    return True
            except Exception as e:
                print(e)
                return False
        else:
            return False


    def get_all_events(self, house):
        events = Event.objects.filter(house=house, deleted=False)
        return events


    def get(self, request, *args, **kwargs):

        context = {}
        house = self.get_house(kwargs["slug"])
        all_events = self.get_all_events(house)
        active_events = all_events.filter(active=True)
        donation_types = DonationType.objects.filter(house=house, deleted=False).order_by("-updated_at")[:2]
        recordings = EventLiveArchive.objects.filter(event_live__event__house=house, event_live__event__allow_non_ticket_archive_viewers=True).order_by("-created_at")[:2]
 
        result_list = sorted(chain(active_events, donation_types, recordings), key=attrgetter('updated_at'))
        result_list.reverse()
        print(result_list)

        owner = self.check_if_user_is_owner(house)
        subscribed = self.check_if_user_is_subscribed(house)

        context["show_events"] = all_events.exists()
        context["recordings"] = recordings.exists()
        context["subscribed"] = subscribed
        context["owner"] = owner
        context["house"] = house
        context["active_events"] = active_events.exists()
        context["result_list"] = result_list

        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        data = request.POST

        json_data = json.loads(request.body)

        house = self.get_house(kwargs["slug"])
        print(json_data)

        # If user is subscribed - they can unsubscribe
        # subscribed = false
        # subscribe = true
        if json_data:
            value = json_data['subscribe_trigger']
            print(value)

            profile = request.user

            if value:
                print('The value is true')
                try:
                    subscriber = Subscriber.objects.get(profile=profile, house=house)
                    subscriber.unsubscribed = False
                    subscriber.save()
                except:
                    subscriber = Subscriber.objects.create(
                        profile=profile, house=event.house, total_events_since_subscribed=0, event_attendance=0, total_campaigns_since_subscribed=0,
                        campaign_views=0, times_donated=0, highest_amount_donated=decimal.Decimal('0.00'))

                html = render_to_string('houses/unsubscribe.html')

            else:
                print("The value is false")
                try:
                    subscriber = Subscriber.objects.get(profile=profile, house=house)
                    subscriber.unsubscribed = True
                    subscriber.save()
                except:
                    subscriber = Subscriber.objects.create(
                        profile=profile, house=event.house, total_events_since_subscribed=0, event_attendance=0, total_campaigns_since_subscribed=0,
                        campaign_views=0, times_donated=0, highest_amount_donated=decimal.Decimal('0.00'), unsubscribed=True)
                html = render_to_string('houses/subscribe.html')

            return JsonResponse({'html': html})

    
        else:
            view_name = "houses:home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))




class HouseContactPageView(FormView):
    model = House
    template_name = "houses/house_contact.html"

    def get_success_url(self):
        view_name = "house_contact"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get_house(self, slug):
        try:
            house = House.objects.get(slug=slug)
            return house
        except:
            raise Http404 

    def check_if_user_is_owner(self, house):
        user = self.request.user
        if user.is_anonymous:
            return False
        house_users = HouseUser.objects.filter(profile=user, house=house)
        print(house_users)
        if house_users.exists():
            return True
        else:
            return False


    def get(self, request, *args, **kwargs):

        context = {}
        house = self.get_house(kwargs["slug"])
        owner = self.check_if_user_is_owner(house)
        form = HouseContactForm()

        context["form"] = form
        context["owner"] = owner
        context["house"] = house
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        form = HouseContactForm(data=data)
        if 'g-recaptcha-response' in data:
            if data['g-recaptcha-response'] == '':
                form.add_error(None, 'Please confirm you are human.')
                return self.form_invalid(form)
            if form.is_valid():
                return self.form_valid(form, request)
            else:
                return self.form_invalid(form)
        else:
            form.add_error(None, 'Please confirm you are human.')
            return self.form_invalid(form)

    def form_valid(self, form, request):
        name = form.cleaned_data["name"]
        message = form.cleaned_data["message"]
        email = form.cleaned_data["email"]
        mail = self.send_email(name, message, email)
        messages.success(request, 'Message Sent!')
        valid_data = super(HouseContactPageView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


    def send_email(self, name, message, email):
        house = self.get_house(self.kwargs["slug"])
        subject = f"New Message from {name}"
        context = {}
        context["name"] = name
        context["message"] = message
        html_message = render_to_string('emails/error_report.html', context)
        plain_message = strip_tags(html_message)
        from_email = f'{name} <{email}>'
        to = [house.email]
        mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
        return "Done"











class HouseSupportInfoView(HouseAccountMixin, FormView):
    model = House
    template_name = "houses/support_info.html"

    def get_success_url(self):
        view_name = "houses:dashboard"
        return reverse(view_name)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        form = HouseSupportInfoForm(instance=house)

        context["form"] = form
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        house = self.get_house()

        form = HouseSupportInfoForm(instance=house, data=request.POST)
        if form.is_valid():

            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)


    def form_valid(self, form, request):
        house = self.get_house()
        self.object = form.save()
        messages.info(request, 'Contact Info Updated')
        valid_data = super(HouseSupportInfoView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))






class HouseVerificationView(HouseAccountMixin, FormView):
    model = House
    template_name = "houses/verification.html"

    def get_success_url(self):
        house = self.get_house()
        view_name = "houses:verify"
        return reverse(view_name)

    def get(self, request, *args, **kwargs):
        house = self.get_house()
        
        # try:
        #     house_director = HouseDirector.objects.get(house=house)
        #     return HttpResponseRedirect(self.get_success_url())
        # except:
        #     pass

        if house.address_entered:
            form = HouseDirectorForm()
        elif house.house_type:
            form = HouseVerificationForm(instance=house)
        else:
            form = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        profile = self.request.user
        current_house_user = HouseUser.objects.get(profile=profile, house=house)
        house_directors = HouseDirector.objects.filter(house=house)

        context["house_directors"] = house_directors
        context["form"] = form
        context["current_house_user"] = current_house_user
        context["profile"] = profile
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        house = self.get_house()

        # Step 1 - User chooses entity type
        if 'house_type' in data:
            house.house_type = data["house_type"]
            house.save()
            messages.info(request, '%s House Chosen' % (data["house_type"]))
            return HttpResponseRedirect(self.get_success_url())

        # If we have the house type and address
        if house.address_entered:
            form = HouseDirectorForm(request.POST, request.FILES)

        # If we only have the house type and need the address
        elif house.house_type:
            form = HouseVerificationForm(instance=house, data=data)

        # If we don't have the house type yet
        else:
            form = None

        if form:
            if form.is_valid():
                return self.form_valid(form, request)
            else:
                return self.form_invalid(form)

    def form_valid(self, form, request):
        house = self.get_house()

        # If we are validating the director form
        if house.address_entered:
            form.instance.house = house
            house.verification_pending = True
            house.save()
            self.object = form.save()

            # Send Message To Admins
            account_sid = settings.ACCOUNT_SID
            auth_token = settings.AUTH_TOKEN
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                        body="%s has requested a verification. Verification type: %s.\n- Arqam House" % (house.name, house.house_type),
                        from_='+16475571902',
                        to='+16472985582'
                    )
            
        # If we are adding the house address
        else:
            self.object = form.save()
            messages.info(request, 'Tax Information Updated')
        
        valid_data = super(HouseVerificationView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


    



# Create your views here.
class DashboardView(HouseAccountMixin, DetailView):
    model = House
    template_name = "houses/house_dashboard.html"

    def graph_data(self, house):
        
        transactions = Transaction.objects.filter(house=house)
        today = timezone.now()
        days_earlier = today - timedelta(days=10)
        day_label = []
        sales_label = []

        for x in range(10):
            one_day_earlier = today - timedelta(days=x)
            transactions_for_day = transactions.filter(created_at__day=one_day_earlier.day, created_at__month=one_day_earlier.month, created_at__year=one_day_earlier.year)

            sales_sum = 0
            for transaction in transactions_for_day:
                if transaction.house_amount:
                    sales_sum += transaction.house_amount
                else:
                    sales_sum += decimal.Decimal(0.00)

            sales_label.append('{0:.2f}'.format(sales_sum))
            day_label.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))

        
        sales_label = list(reversed(sales_label))
        day_label = list(reversed(day_label))

        graph_data = {'sales_label':sales_label, 'day_label':day_label}
        return graph_data


    def get(self, request, *args, **kwargs):

        context = {}
        house = self.get_house()
        house_balance = HouseBalance.objects.get(house=house)
        events = self.get_events()
        profile = self.get_profile()

        graph_data = self.graph_data(house)

        context["payout_set"] = PayoutSetting.objects.filter(house=house).exists()
        context["house_balance"] = house_balance
        context["graph_data"] = graph_data
        context["house"] = house
        context["dashboard_events"] = events
        context["profile"] = profile
        context["dashboard_tab"] = True

        return render(request, self.template_name, context)



class HouseLandingView(HouseLandingMixin, DetailView):
    model = House
    template_name = "houses/house_landing.html"

    def get(self, request, *args, **kwargs):
        context = {}
        slug = self.kwargs['slug']
        House = self.get_House(slug)
        if not House:
            raise Http404
        users = self.get_users(House)
        print(users)
        profiles = self.get_profiles(users)

        context["profiles"] = profiles
        context["users"] = users
        context["House"] = House
        return render(request, self.template_name, context)


class HouseUserDetailView(HouseAccountMixin, UpdateView):
    model = HouseUser
    form_class = HouseUserOptionsForm
    template_name = "houses/house_user_detail.html"

    def get_success_url(self):
        view_name = "houses:manage"
        return reverse(view_name)

    def get_house_user(self):
        pk = self.kwargs["pk"]
        house_user = HouseUser.objects.get(id=pk)
        return house_user

    def get(self, request, *args, **kwargs):
        self.object = self.get_house_user()
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        form = HouseUserOptionsForm(instance=self.object)

        context["house_user"] = self.object
        context["form"] = form
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        self.object = self.get_house_user()

        print(data)
        if 'Remove' in data:
            house_user_id = data["Remove"]
            house_user_to_remove = HouseUser.objects.get(id=house_user_id)
            house_user_to_remove.profile.house = None
            house_user_to_remove.profile.save()
            house_user_to_remove.delete()
            messages.info(request, 'User removed from house.')
            return HttpResponseRedirect(self.get_success_url())

        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        self.object = form.save()
        messages.success(request, 'House User Preferences Updated!')
        valid_data = super(HouseUserDetailView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



class AddUserToHouseView(HouseAccountMixin, FormView):

    template_name = "houses/manage_users.html"

    def get_success_url(self):
        view_name = "houses:manage"
        return reverse(view_name)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        profile = self.request.user
        house_users = HouseUser.objects.filter(house=house)
        context["house_users"] = house_users
        context["form"] = AddUserToHouse()
        context["profile"] = profile
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST

        form = AddUserToHouse(data=data)
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        print(form.cleaned_data)
        email = form.cleaned_data["email"]
        profile = self.request.user
        house = self.get_house()

        # Step 1 - See if user exists
        try:
            profile_to_add = Profile.objects.get(email=email)

            # Step 2 - If user exists make sure the user isnt already added
            try:
                house_user = HouseUser.objects.get(profile=profile_to_add, house=house)
                messages.warning(request, 'This user is already a member of your house.')
            except Exception as e:
                print(e)
                house_user = HouseUser.objects.create(profile=profile_to_add, house=house, role='admin')
                if not profile_to_add.house:
                    profile_to_add.house = house
                    profile_to_add.save()
                messages.success(request, 'New user successfully added!')
        except Exception as e:
            print(e)
            messages.warning(request, 'No such user with that email address.')

        valid_data = super(AddUserToHouseView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))






class HouseUpdateView(HouseAccountMixin, FormView):
    template_name = "houses/house_update.html"

    def get_success_url(self):
        view_name = "houses:update"
        return reverse(view_name)

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        profile = self.request.user
        house_users = HouseUser.objects.filter(profile=profile)

        current_house_user = HouseUser.objects.get(profile=profile, house=house)
        house_change_form = HouseChangeForm(house_users=house_users, initial={"house_select": current_house_user})
        house_logo_form = HouseLogoForm(instance=self.get_house())

        context["house_logo_form"] = house_logo_form
        context["dashboard_events"] = self.get_events()
        context["house_change_form"] = house_change_form
        context["profile"] = profile
        context["house"] = house

        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = request.POST
        house = self.get_house()

        if 'house_user' in data:
            house_user = HouseUser.objects.get(id=data["house_user"])
            profile = self.request.user
            profile.house = house_user.house
            profile.save()
            messages.success(request, 'You have changed your house to  %s!' % (house_user.house))
            return HttpResponse("/house/update")

        if 'Remove' in data:
            house.logo = None
            house.save()
            messages.warning(request, 'Event image successfully removed')
        
        house_logo_form = HouseLogoForm(data, request.FILES, instance=self.get_house())

        if house_logo_form.is_valid():
            return self.form_valid(house_logo_form, request, house)
        else:
            messages.warning(request, 'Error updating logo')
            return self.form_invalid(house_logo_form)

    def form_valid(self, form, request, house):
        house = form.save()
        house.save()
        valid_data = super(HouseUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    template_name = "houses/house_create.html"

    def get_success_url(self):
        view_name = "houses:dashboard"
        return reverse(view_name)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        context["form"] = form
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        profile = self.request.user
        print(profile)
        initial_location_data = {"country":profile.country, "region":profile.region, "city":profile.city}
        form = HouseForm(initial=initial_location_data)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = HouseForm(data, request.FILES)
        if form.is_valid():
            messages.success(request, 'House Created!')
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)


    def form_valid(self, form, request):
        
        # Save the House
        self.object = form.save()

        # get profile
        profile = request.user

        # Create Selected House object and assign this House
        profile.house = self.object
        profile.save()
        
        # Create House User
        house_user = HouseUser.objects.create(house=self.object, profile=profile, role="admin",)
        house_user.save()

        # Create House Balance and initial House Balance Log with $0.00 opening balance
        house_balance = HouseBalance.objects.create(house=self.object, balance=0.00)
        house_balance.save()
        house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, balance=0.00, opening_balance=True, gross_balance=0.00)
        house_balance_log.save()

        self.send_text_message(self.object)

        valid_data = super(HouseCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


    def send_text_message(self, house):
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        message = client.messages.create(
                    body="A New House Was Created!\nHouse Name: %s\n- Arqam House" % (house.name),
                    from_='+16475571902',
                    to='+16472985582'
                )

















