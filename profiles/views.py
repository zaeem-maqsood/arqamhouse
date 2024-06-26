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

from itertools import chain
from operator import attrgetter

from subscribers.models import Subscriber
from .models import Profile, Address
from .forms import (ProfileForm, LoginForm, ProfileUpdateForm, ProfileChangePasswordForm, ProfileAlreadyExistsForm, 
                    ProfileVerifcationForm, ProfileChangePhoneForm, AddressForm)
from .mixins import ProfileMixin
from cities_light.models import City, Region, Country
from events.models import Event, EventOrder, EventLiveArchive
from donations.models import Donation, DonationType


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
        donation_types = DonationType.objects.filter(house__in=houses, deleted=False).order_by("-updated_at")[:4]
        recordings = EventLiveArchive.objects.filter(event_live__event__house__in=houses).order_by("-created_at")[:2]
 
        result_list = sorted(chain(events, donation_types, recordings), key=attrgetter('updated_at'))
        result_list.reverse()
        print(result_list)

        return result_list

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        if not profile.verified:
            return redirect('profiles:verification')
        house = self.check_for_house(profile)
        context["house"] = house
        context["profile"] = profile
        context["result_list"] = self.get_updates(profile)
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








class AddAddress(CreateView):
    model = Address
    form_class = AddressForm
    template_name = "profiles/address.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "profiles:address_list"
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
        default = form.cleaned_data.get("default")
        profile = self.get_profile()
        
        if default:
            addresses = Address.objects.filter(profile=profile)
            for address in addresses:
                address.default = False
                address.save()

        print(default)
        form.instance.profile = profile
        self.object = form.save()
        messages.success(request, "Address Created")
        valid_data = super(AddAddress, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



class UpdateAddress(UpdateView):
    model = Address
    form_class = AddressForm
    template_name = "profiles/update_address.html"

    def get_address(self, profile):
        try:
            address = Address.objects.get(profile=profile, id=self.kwargs["id"])
            return address
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        self.object = self.get_address(profile)
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):

        if 'postcard' in self.request.GET:
            view_name = "postcards:order_view_senders"

            if 'recep' in self.request.GET:
                return f"{reverse(view_name, kwargs={'slug': self.request.GET['postcard']})}?recep={self.request.GET['recep']}"
            else:
                return reverse(view_name, kwargs={"slug": self.request.GET["postcard"]})

        view_name = "profiles:address_list"
        return reverse(view_name)

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            raise Http404

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        self.object = self.get_address(profile)
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
        default = form.cleaned_data.get("default")
        profile = self.get_profile()
        
        if default:
            addresses = Address.objects.filter(profile=profile)
            for address in addresses:
                address.default = False
                address.save()

        print(default)
        self.object = form.save()
        messages.success(request, "Address Updated")
        valid_data = super(UpdateAddress, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



# Create your views here.
class AddressList(View):

    template_name = "profiles/address_list.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        addresses = Address.objects.filter(profile=profile).order_by("-default")
        context["addresses"] = addresses
        context["profile"] = profile
        return render(request, self.template_name, context)





class ProfileCreateView(FormView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_create.html"

    def get_success_url(self):
        view_name = "dashboard"
        return reverse(view_name)

    def get_context_data(self, form, request, *args, **kwargs):
        context = {}
        context["form"] = form
        return context


    def get(self, request, *args, **kwargs):
        self.object = None

        # if request.user.is_authenticated:
        #     return redirect(':verification')
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

        apt_number = form.cleaned_data.get("apt_number")
        street_number = form.cleaned_data.get("street_number")
        route = form.cleaned_data.get("route")
        locality = form.cleaned_data.get("locality")
        administrative_area_level_1 = form.cleaned_data.get("administrative_area_level_1")
        address = form.cleaned_data.get("address")
        postal_code = form.cleaned_data.get("postal_code")

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

                address_object = Address.objects.create(profile=profile)
                address_object.address = address
                address_object.apt_number = apt_number
                address_object.street_number = street_number
                address_object.route = route
                address_object.locality = locality
                address_object.administrative_area_level_1 = administrative_area_level_1
                address_object.postal_code = postal_code
                profile.save()
                address_object.save()

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
            address_object = Address.objects.create(profile=self.object)
            address_object.address = form.cleaned_data.get("address")
            address_object.apt_number = form.cleaned_data.get("apt_number")
            address_object.street_number = form.cleaned_data.get("street_number")
            address_object.route = form.cleaned_data.get("route")
            address_object.locality = form.cleaned_data.get("locality")
            address_object.administrative_area_level_1 = form.cleaned_data.get("administrative_area_level_1")
            address_object.postal_code = form.cleaned_data.get("postal_code")
            address_object.save()

            login(request, self.object)
        
        # account_sid = settings.ACCOUNT_SID
        # auth_token = settings.AUTH_TOKEN
        # client = Client(account_sid, auth_token)
        # service_id = "VAc350a17577cac4548f9dc591cbc1e950"
        # verification = client.verify.services(service_id).verifications.create(to=str(phone), channel='sms')
        # print(verification.status)
        # status = verification.status

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
        try:
            verification_check = client.verify.services(service_id).verification_checks.create(to=str(profile.phone), code=str(verification_number))
            print(verification_check.status)

            if verification_check.status == 'approved':
                profile.verified = True
                profile.save()
        except Exception as e:
            print(e)
            form.add_error(None, "There was an issue with your code. Please try again.")
            return self.render_to_response(self.get_context_data(form=form))

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
            view_name = "dashboard"
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
            return redirect('dashboard')

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
                    print("It came here son")
                    self.success_url = reverse('dashboard')

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







