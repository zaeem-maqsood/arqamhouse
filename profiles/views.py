# Bismillah, In the name of God

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import RedirectView
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from houses.mixins import HouseAccountMixin

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.utils.html import strip_tags
from django.core import mail


from subscribers.models import Subscriber
from .models import Profile
from .forms import ProfileForm, LoginForm, ProfileUpdateForm, ProfileChangePasswordForm, ProfileAlreadyExistsForm
from .mixins import ProfileMixin
from cities_light.models import City, Region, Country
from events.models import Event, EventOrder


class PasswordChangeView(ProfileMixin, FormView):
    model = Profile
    template_name = "profiles/change_password.html"

    def get_success_url(self):
        view_name = "profiles:dashboard"
        return reverse(view_name)

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

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
    region_id = request.GET.get('region')
    cities = City.objects.filter(region__id=region_id).order_by('name')
    return render(request, 'components/city_dropdown_list_options.html', {'cities': cities})


def load_regions(request):
    country_id = request.GET.get('country')
    regions = Region.objects.filter(country__id=country_id).order_by('name')
    return render(request, 'components/region_dropdown_list_options.html', {'regions': regions})




class UserOrdersView(ProfileMixin, View):
    template_name = "profiles/orders.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        orders = EventOrder.objects.filter(email=profile.email).order_by("-created_at")
        print(orders)
        context["orders"] = orders
        context["profile"] = profile
        return render(request, self.template_name, context)




class UserSubscribersView(ProfileMixin, View):
    template_name = "profiles/subscribers.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        subscribers = Subscriber.objects.filter(profile=profile, unsubscribed=False)
        print(subscribers)
        context["subscribers"] = subscribers
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

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
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
        view_name = "profiles:dashboard"
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
                print("Did it come here")
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
                profile.save()



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

            # Uncomment this when we want email activation again
            # current_site = get_current_site(request)
            # subject = 'Finish Activating Your Account'
            # context = {}
            # context["name"] = name
            # context["user"] = self.object
            # context["domain"] = current_site.domain
            # context["uid"] = urlsafe_base64_encode(force_bytes(self.object.pk))
            # context["token"] = account_activation_token.make_token(self.object)
            # html_message = render_to_string('emails/account_activation.html', context)
            # plain_message = strip_tags(html_message)
            # from_email = 'Arqam House <info@arqamhouse.com>'
            # to = [email]
            # mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
            # messages.success(request, 'Account Created! Please check your email to finish activation.')

        messages.success(request, 'Account Created! Login to continue.')

        valid_data = super(ProfileCreateView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print(form.errors)
        print(form.non_field_errors)
        return self.render_to_response(self.get_context_data(form=form, request=request))





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
        view_name = "profiles:update"
        return reverse(view_name)


    def get_context_data(self, request, *args, **kwargs):
        context = {}
        form = self.get_form()
        profile = self.get_profile()
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
            messages.success(request, 'Profile Updated!')
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







