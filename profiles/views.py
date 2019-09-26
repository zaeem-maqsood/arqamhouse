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


from .models import Profile
from .forms import ProfileForm, LoginForm, ProfileUpdateForm
from .mixins import ProfileMixin
from cities_light.models import City, Region, Country




def load_cities(request):
	region_id = request.GET.get('region')
	cities = City.objects.filter(region__id=region_id).order_by('name')
	return render(request, 'components/city_dropdown_list_options.html', {'cities': cities})


def load_regions(request):
	country_id = request.GET.get('country')
	regions = Region.objects.filter(country__id=country_id).order_by('name')
	return render(request, 'components/region_dropdown_list_options.html', {'regions': regions})



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


	def get(self, request, *args, **kwargs):
		context = {}
		profile = request.user
		print(profile)
		print(profile.house)
		house = self.check_for_house(profile)
		print(house)
		if house:
			view_name = "houses:dashboard"
			return HttpResponseRedirect(reverse(view_name))
		context["profile"] = profile
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


class ProfileCreateView(CreateView):
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
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form, request)


	def form_valid(self, form, request):
		
		# Get email and password from the form
		email = form.cleaned_data.get("email")
		password = form.cleaned_data.get("password")
		name = form.cleaned_data.get("name")
		country = form.cleaned_data.get("country")
		region = form.cleaned_data.get("region")
		city = form.cleaned_data.get("city")

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
		self.object.is_active = False
		self.object.save()

		current_site = get_current_site(request)
		subject = 'Finish Activating Your Account'
		context = {}
		context["name"] = name
		context["user"] = self.object
		context["domain"] = current_site.domain
		context["uid"] = urlsafe_base64_encode(force_bytes(self.object.pk))
		context["token"] = account_activation_token.make_token(self.object)
		html_message = render_to_string('emails/account_activation.html', context)
		plain_message = strip_tags(html_message)
		from_email = 'Arqam House <info@arqamhouse.com>'
		to = [email]
		mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)

		messages.success(request, 'Account Created! Please check your email to finish activation.')

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
	success_url = None


	def get_context_data(self, form, *args, **kwargs):
		context = {}
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		# Make sure user already not logged in
		try:
			next_page = request.GET['next']
			if next_page:
				self.success_url = next_page
		except:
			self.success_url = 'profiles:dashboard'

		print("Get Call")

		user = self.request.user
		if user.is_anonymous:
			form = self.get_form()
		else:
			return redirect('profiles:dashboard')

		return self.render_to_response(self.get_context_data(form))


	def post(self, request, *args, **kwargs):

		try:
			next_page = request.GET['next']
			if next_page:
				self.success_url = next_page
		except:
			self.success_url = reverse('profiles:dashboard')

		
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form, request)


	def form_valid(self, form, request):
		
		# Get email and password from the form
		email = form.cleaned_data.get("email")
		password = form.cleaned_data.get("password")

		# Authenticate user with this email and password
		try:
			print("Came to Login")
			print(email)
			print(password)
			profile = authenticate(request, username=None, email=email, password=password)
			print(profile)
		except Exception as e:
			print(e)
			form.add_error("email", "Invalid username/password combination")
			return self.render_to_response(self.get_context_data(form=form))
		
		# Make sure user is authenticated, log them in or diplay 404 error
		if profile is not None:
			login(request, profile)
		else:
			form.add_error("email", "Please check your email to finish activating your account. If you need another email choose 'Recover Account'")
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







