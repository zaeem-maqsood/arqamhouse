# Bismillah, In the name of God
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import RedirectView
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from houses.mixins import HouseAccountMixin

from twilio.rest import Client

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.utils.html import strip_tags
from django.core import mail


from subscribers.models import Subscriber
from .models import Profile
from .forms import ProfileForm, LoginForm, ProfileUpdateForm, ProfileChangePasswordForm, ProfileAlreadyExistsForm, ProfileVerifcationForm, ProfileChangePhoneForm
from .mixins import ProfileMixin
from cities_light.models import City, Region, Country
from events.models import Event, EventOrder
from donations.models import Donation


class PasswordChangeView(ProfileMixin, FormView):
    model = Profile
    template_name = "profiles/change_password.html"

    def get_success_url(self):
        view_name = "profiles:dashboard"
        return reverse(view_name)

    def get_context_data(self, form, request, *args, **kwargs):
        context = {}
        profile = request.user
        context["profile"] = profile
        context["form"] = form
        return context

    def get(self, request, *args, **kwargs):
        form = ProfileChangePasswordForm()
        return self.render_to_response(self.get_context_data(form, request))

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = ProfileChangePasswordForm(data)
        if form.is_valid():
            messages.success(request, 'Profile Updated!')
            return self.form_valid(form)
        else:
            return self.form_invalid(form, request)

    def form_valid(self, form):
        print(form.cleaned_data)
        password = form.cleaned_data.get("password")
        print(password)
        profile = self.get_profile()
        profile.set_password(password)
        profile.temp_password = None
        profile.save()
        valid_data = super(PasswordChangeView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form, request):
        print("Didint work")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form, request=request))



def load_cities(request):
    json_data = json.loads(request.body)
    if json_data:
        print(json_data)
        region_id = json_data['region_id']
        cities = City.objects.filter(region__id=region_id).order_by('name')
        print(cities)
        html = render_to_string('components/city_dropdown_list_options.html', {'cities': cities})
        return JsonResponse({'html': html})


def load_regions(request):
    json_data = json.loads(request.body)
    if json_data:
        print(json_data)
        regions = Region.objects.filter(country__id=country_id).order_by('name')
        html = render_to_string('components/region_dropdown_list_options.html', {'regions': regions})
        return JsonResponse({'html': html})




class UserOrdersView(ProfileMixin, View):
    template_name = "profiles/tickets.html"

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()

        if not profile.verified:
            return redirect('profiles:verification')

        orders = EventOrder.objects.filter(email=profile.email).order_by("-created_at")
        print(orders)
        context["orders"] = orders
        context["profile"] = profile
        return render(request, self.template_name, context)




class UserDonationsView(ProfileMixin, View):
    template_name = "profiles/donations.html"


    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()

        if not profile.verified:
            return redirect('profiles:verification')

        donations = Donation.objects.filter(email=profile.email).order_by("-created_at")
        print(donations)
        context["donations"] = donations
        context["profile"] = profile
        return render(request, self.template_name, context)




class UserSubscribersView(ProfileMixin, View):
    template_name = "profiles/subscribers.html"

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()

        # Make sure user is verified 
        if not profile.verified:
            return redirect('profiles:verification')

        subscribers = Subscriber.objects.filter(profile=profile, unsubscribed=False)
        print(subscribers)
        context["subscribers"] = subscribers
        context["profile"] = profile
        return render(request, self.template_name, context)




class UserMenuPage(ProfileMixin, View):
    template_name = "profiles/menu.html"

    def check_for_house(self, profile):
        try:
            house = profile.house
            return house
        except Exception as e:
            print(e)
            print("Did it come here")
            return None

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        if not profile.verified:
            return redirect('profiles:verification')

        house = self.check_for_house(profile)
        context["house"] = house
        context["profile"] = profile
        return render(request, self.template_name, context)









class UserDashboardView(ProfileMixin, View):
    model = Profile
    template_name = "profiles/dashboard.html"

    def check_for_house(self, profile):
        try:
            house = profile.house
            return house
        except Exception as e:
            print(e)
            print("Did it come here")
            return None


    def get_updates(self, profile):
        subscriptions = Subscriber.objects.select_related('house').filter(profile=profile, unsubscribed=False)
        print(subscriptions)
        houses = []
        for subscription in subscriptions:
            houses.append(subscription.house)
        events = Event.objects.filter(house__in=houses, deleted=False, active=True)
        return events

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        if not profile.verified:
            return redirect('profiles:verification')
        house = self.check_for_house(profile)
        context["profile"] = profile
        context["events"] = self.get_updates(profile)
        return render(request, self.template_name, context)


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = Profile.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse('profiles:login'))
    else:
        return HttpResponseRedirect(reverse('profiles:login'))





class ProfileCreateView(FormView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_create.html"

    def get_success_url(self):
        view_name = "profiles:verification"
        return reverse(view_name)

    def get_context_data(self, form, request, *args, **kwargs):
        context = {}
        context["form"] = form
        return context


    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form, request=request))


    def post(self, request, *args, **kwargs):
        data = request.POST

        email = data['email']
        email = email.lower()
        print(f"the email is {email}")

        already_exists = False

        try:
            profile = Profile.objects.get(email=email)
            if profile.temp_password:
                form = ProfileAlreadyExistsForm(data, request.FILES, instance=profile)
                already_exists = True
            else:
                 form = self.get_form()
        except:
            form = self.get_form()


        if form.is_valid():
            return self.form_valid(form, request, already_exists)
        else:
            return self.form_invalid(form, request)

    def form_valid(self, form, request, already_exists):

        # Get email and password from the form
        email = form.cleaned_data.get("email")
        name = form.cleaned_data.get("name")
        country = form.cleaned_data.get("country")
        region = form.cleaned_data.get("region")
        city = form.cleaned_data.get("city")

        phone = form.cleaned_data.get("phone")
    
        print(phone)

        email = email.lower()


        if already_exists:

            try:
                profile = Profile.objects.get(email=email)
            except Exception as e:
                print(e)
                print("errors")


            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")

            if password1 != password2:
                form.add_error("email", "Password don't match!")
                return self.render_to_response(self.get_context_data(form=form, request=request))

            else:
                profile.set_password(password1)
                profile.temp_password = None
                profile.phone = phone
                profile.region = region
                profile.city = city
                profile.save()

            login(request, profile)

        else:

            password = form.cleaned_data.get("password")

            # Create a user with this email and password
            try:
                profile = Profile.objects.get(email=email)
                form.add_error("email", "It seems this email is already in use, please login or use a different email.")
                return self.render_to_response(self.get_context_data(form=form, request=request))
            except Exception as e:
                print(e)
                print("errors")

            # Save form
            self.object = form.save(commit=False)
            self.object.email = email.lower()
            self.object.is_active = True #Change this to false and when we want email authntication again.
            self.object.save()

            login(request, self.object)

        messages.success(request, 'Account Created! Login to continue.')

        
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        service_id = "VAc350a17577cac4548f9dc591cbc1e950"
        verification = client.verify.services(service_id).verifications.create(to=str(phone), channel='sms')
        print(verification.status)
        status = verification.status

        valid_data = super(ProfileCreateView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print(form.errors)
        print(form.non_field_errors)
        return self.render_to_response(self.get_context_data(form=form, request=request))


class VerificationView(ProfileMixin, FormView):
    template_name = 'profiles/verification.html'

    def get_success_url(self):
        view_name = "profiles:dashboard"
        return reverse(view_name)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        context["form"] = form
        context["profile"] = self.get_profile()
        return context

    def get(self, request, *args, **kwargs):
        # Make sure user already not logged in
        profile = self.get_profile()
        if not profile.phone:
            return redirect('profiles:change_phone')
        print(request.user)
        form = ProfileVerifcationForm()

        return self.render_to_response(self.get_context_data(form))


    def post(self, request, *args, **kwargs):
        data = request.POST
        profile = self.get_profile()

        print(data)
        if not data:
            json_data = json.loads(request.body)
            if json_data:
                print(json_data)
                refresh_code = json_data['refresh_code']
                account_sid = settings.ACCOUNT_SID
                auth_token = settings.AUTH_TOKEN
                client = Client(account_sid, auth_token)
                service_id = "VAc350a17577cac4548f9dc591cbc1e950"
                verification = client.verify.services(service_id).verifications.create(to=str(profile.phone), channel='sms')
                print(verification.status)
                status = verification.status
                return JsonResponse({"done": True})


        form = ProfileVerifcationForm(data=data)
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)


    def form_valid(self, form, request):
        profile = self.get_profile()
        verification_number = form.cleaned_data.get("verification_number")
        
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        service_id = "VAc350a17577cac4548f9dc591cbc1e950"
        verification_check = client.verify.services(service_id).verification_checks.create(to=str(profile.phone), code=str(verification_number))
        print(verification_check.status)

        if verification_check.status == 'approved':
            profile.verified = True
            profile.save()

        valid_data = super(VerificationView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form, request):
        print(form.errors)
        print(form.non_field_errors)
        return self.render_to_response(self.get_context_data(form=form))



class ChangePhoneNumberView(ProfileMixin, FormView):
    template_name = 'profiles/change_phone.html'

    def get_success_url(self):
        view_name = "profiles:dashboard"
        return reverse(view_name)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        context["form"] = form
        context["profile"] = self.get_profile()
        return context

    def get(self, request, *args, **kwargs):
        # Make sure user already not logged in
        
        print(request.user)
        form = ProfileChangePhoneForm()

        return self.render_to_response(self.get_context_data(form))

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = ProfileChangePhoneForm(data=data)
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)

    def form_valid(self, form, request):
        
        phone = form.cleaned_data.get("phone")
        profile = self.get_profile()
        profile.phone = phone
        profile.verified = False
        profile.save()

        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        service_id = "VAc350a17577cac4548f9dc591cbc1e950"
        verification = client.verify.services(service_id).verifications.create(to=str(profile.phone), channel='sms')
        print(verification.status)
        status = verification.status

        valid_data = super(ChangePhoneNumberView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print(form.errors)
        print(form.non_field_errors)
        return self.render_to_response(self.get_context_data(form=form))





# Create your views here.
class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return self.get_success_url()

    def get_success_url(self):
        view_name = "profiles:login"
        return HttpResponseRedirect(reverse(view_name))



class LoginView(FormView):
    template_name = 'profiles/login.html'
    form_class = LoginForm
    
    def get_success_url(self):

        if 'next' in self.request.GET:
            return self.request.GET['next']
        else:
            view_name = "profiles:dashboard"
            return reverse(view_name)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        context["form"] = form
        return context

    def get(self, request, *args, **kwargs):
        # Make sure user already not logged in

        user = self.request.user
        if user.is_anonymous:
            form = self.get_form()
        else:
            if user.house:
                return redirect('houses:dashboard')
            else:
                return redirect('profiles:dashboard')

        return self.render_to_response(self.get_context_data(form))


    def post(self, request, *args, **kwargs):
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)


    def form_valid(self, form, request):
        
        # Get email and password from the form
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        email = email.lower()

        # Added this bit of code because some users signed up with capital letters in their email
        try:
            profile_getter = Profile.objects.get(email=email)
            
            if profile_getter.temp_password:
                form.add_error("email", "Please create an account to continue.")
                return self.render_to_response(self.get_context_data(form=form))
        except Exception as e:
            print(e)

        # Authenticate user with this email and password
        try:
            profile = authenticate(request, username=None, email=email, password=password)
            if profile == None:
                form.add_error("email", "Invalid username/password combination")
                return self.render_to_response(self.get_context_data(form=form))
            else:
                login(request, profile)
                try:
                    next_page = request.GET['next']
                    self.success_url = next_page
                except:
                    if profile.house:
                        print("It came here son")
                        self.success_url = reverse('houses:dashboard')

        except Exception as e:
            print(e)
            form.add_error("email", "Invalid username/password combination")
            return self.render_to_response(self.get_context_data(form=form))
        

        valid_data = super(LoginView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        return self.render_to_response(self.get_context_data(form=form))






class ProfileUpdateView(HouseAccountMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = "profiles/profile_update.html"

    def get_success_url(self):
        view_name = "profiles:menu"
        return reverse(view_name)


    def get_context_data(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        form = self.get_form()
        context["profile"] = profile
        context["form"] = form
        return context


    def get(self, request, *args, **kwargs):
        self.object = self.get_profile()
        return self.render_to_response(self.get_context_data(request))


    def post(self, request, *args, **kwargs):
        data = request.POST
        self.object = self.get_profile()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, request)


    def form_valid(self, form):
        self.object = form.save()
        valid_data = super(ProfileUpdateView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print("Didint work")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form, request=request))







