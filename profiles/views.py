from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import RedirectView
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from organizations.mixins import OrganizationAccountMixin

from django.contrib.auth.models import User
from .models import Profile, SelectedOrganization
from .forms import ProfileForm, LoginForm
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

	def check_for_organization(self, user):
		try:
			selected_organization = SelectedOrganization.objects.get(user=user)
			organization = selected_organization.organization
			return organization
		except Exception as e:
			print(e)
			return None

	def get_profile(self, user):
		try:
			profile = Profile.objects.get(user=user)
			print(profile)
		except Exception as e:
			print("This")
			print(e)
			print("This")
			raise Http404
		return profile

	def get(self, request, *args, **kwargs):
		context = {}
		user = request.user
		profile = self.get_profile(user)
		organization = self.check_for_organization(user)
		if organization:
			view_name = "organizations:dashboard"
			return HttpResponseRedirect(reverse(view_name, kwargs={'slug': organization.slug}))
		context["profile"] = profile
		return render(request, self.template_name, context)



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
			messages.success(request, 'Updated!')
			return self.form_valid(form, request)
		else:
			print(form.errors)
			messages.warning(request, 'There seems to be a problem')
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
			user = User.objects.get(username=email)
			form.add_error("email", "It seems this email is already in use, please login or use a different email.")
			return self.render_to_response(self.get_context_data(form=form, request=request))
		except Exception as e:
			print(e)
			user = User.objects.create_user(email, email, password)

		# Authenticate user 
		user = authenticate(request, username=email, password=password)

		# Make sure user is authenticated, log them in or diplay 404 error
		if user is not None:
			login(request, user)
			messages.success(request, 'Logged in as %s' % (user.username))
		else:
			raise Http404

		# link user to profile
		form.instance.user = user
		
		# Save form
		self.object = form.save()

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

		# Create a user with this email and password
		try:
			user = authenticate(request, username=email, password=password)
		except Exception as e:
			print(e)
			form.add_error("email", "Invalid username/password combination")
			return self.render_to_response(self.get_context_data(form=form))
		
		# Make sure user is authenticated, log them in or diplay 404 error
		if user is not None:
			login(request, user)
			messages.success(request, 'Logged in as %s' % (user.username))
		else:
			print("Error Happended")
			raise Http404

		valid_data = super(LoginView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, request):
		return self.render_to_response(self.get_context_data(form=form))





class ProfileDetailView(ProfileMixin, DetailView):
	model = Profile
	template_name = "profiles/profile_detail.html"

	def get(self, request, *args, **kwargs):
		context = {}
		slug = self.kwargs['slug']
		profile = self.get_profile(slug)
		if not profile:
			raise Http404
		user = self.get_user(profile)
		organizations = self.get_organizations(user)
		does_profile_belong_to_user = self.does_profile_belong_to_user(profile)

		context["does_profile_belong_to_user"] = does_profile_belong_to_user
		context["profile"] = profile
		context["organizations"] = organizations
		return render(request, self.template_name, context)




class ProfileUpdateView(OrganizationAccountMixin, UpdateView):
	model = Profile
	form_class = ProfileForm
	template_name = "profiles/profile_update.html"

	def get_success_url(self):
		slug = self.kwargs['slug']
		view_name = "profiles:update"
		return reverse(view_name, kwargs={"slug": slug})


	def get_context_data(self, request, *args, **kwargs):
		context = {}
		form = self.get_form()
		slug = self.kwargs['slug']
		profile = self.get_profile(slug)
		# if not 
		context["profile"] = profile
		context["form"] = form
		return context


	def get(self, request, *args, **kwargs):
		slug = self.kwargs['slug']
		try:
			profile = Profile.objects.get(slug=slug)
		except:
			raise Http404
		self.object = profile
		return self.render_to_response(self.get_context_data(request))


	def post(self, request, *args, **kwargs):
		data = request.POST

		slug = self.kwargs['slug']
		try:
			profile = Profile.objects.get(slug=slug)
		except:
			raise Http404

		self.object = profile
		form = self.get_form()

		if form.is_valid():
			messages.success(request, 'Updated!')
			return self.form_valid(form)
		else:
			print(form.errors)
			messages.warning(request, 'There seems to be a problem')
			return self.form_invalid(form, request)


	def form_valid(self, form):
		self.object = form.save()
		valid_data = super(ProfileUpdateView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, request):
		print("Didint work")
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, request=request))







