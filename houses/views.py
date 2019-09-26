import stripe
import random
import decimal
import numpy as np
import sys
import time
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
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect

from .mixins import HouseAccountMixin, HouseLandingMixin

from django.contrib.auth.models import User
from profiles.models import Profile
from .models import House, HouseUser
from .forms import AddUserToHouse, HouseUpdateForm, HouseChangeForm, HouseForm

from events.models import Event, Ticket, EventCart, EventCartItem, EventOrder, Attendee
from profiles.models import Profile
from payments.models import HouseBalance, HouseBalanceLog, Transaction, PayoutSetting



# Create your views here.
class DashboardView(HouseAccountMixin, DetailView):
	model = House
	template_name = "houses/house_dashboard.html"

	def graph_data(self, house):
		
		transactions = Transaction.objects.filter(house=house, failed=False)
		today = timezone.now()
		days_earlier = today - timedelta(days=10)
		day_label = []
		sales_label = []

		for x in range(10):
			one_day_earlier = today - timedelta(days=x)
			transactions_for_day = transactions.filter(created_at__day=one_day_earlier.day)

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
		print(graph_data)

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
		current_house_user = HouseUser.objects.get(profile=profile, house=house)
		house_users = HouseUser.objects.filter(house=house).exclude(profile=profile)
		context["current_house_user"] = current_house_user
		context["house_users"] = house_users
		context["form"] = AddUserToHouse()
		context["profile"] = profile
		context["house"] = house
		context["dashboard_events"] = self.get_events()
		return context

	def post(self, request, *args, **kwargs):
		data = request.POST

		print(data)
		if 'Remove' in data:
			house_user_id = data["Remove"]
			house_user_to_remove = HouseUser.objects.get(id=house_user_id).delete()
			messages.info(request, 'User removed from house.')
			return HttpResponseRedirect(self.get_success_url())

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
		print(house_users)
		house_change_form = HouseChangeForm(house_users=house_users, initial={"house_select": current_house_user})
		form = HouseUpdateForm(instance=house)

		context["dashboard_events"] = self.get_events()
		context["house_change_form"] = house_change_form
		context["form"] = form
		context["profile"] = profile
		context["house"] = house

		return context

	def get(self, request, *args, **kwargs):
		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		house = self.get_house()

		print(data)
		if 'house_user' in data:
			house_user = HouseUser.objects.get(id=data["house_user"])
			profile = self.request.user
			profile.house = house_user.house
			profile.save()
			messages.success(request, 'You have changed your house to  %s!' % (house_user.house))
			return HttpResponse("/house/update")

		else:
			profile = self.request.user
			house_users = HouseUser.objects.filter(profile=profile)
			form = HouseUpdateForm(data=data, instance=self.get_house())

			if form.is_valid():
				messages.success(request, 'House Updated!')
				return self.form_valid(form, request, house)
			else:
				messages.warning(request, 'House Name Invalid')
				return self.form_invalid(form)

	def form_valid(self, form, request, house):
		house = form.save()
		house.save()
		valid_data = super(HouseUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))





class HouseCreateView(CreateView):
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
		form = HouseForm(data=data)
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
		house_balance_log = HouseBalanceLog.objects.create(house_balance=house_balance, balance=0.00, opening_balance=True)
		house_balance_log.save()

		valid_data = super(HouseCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))











def merge_images(file1, file2):
	"""Merge two images into one, displayed side by side
	:param file1: path to first image file
	:param file2: path to second image file
	:return: the merged Image object
	"""
	image1 = Image.open(file1)
	image2 = Image.open(file2)

	(width1, height1) = image1.size
	(width2, height2) = image2.size

	result_width = width1 + width2
	result_height = max(height1, height2)

	result = Image.new('RGB', (result_width, result_height))
	result.paste(im=image1, box=(0, 0))
	result.paste(im=image2, box=(width1, 0))
	return result



class ChangeEntityTypeView(HouseAccountMixin, View):

	def get(self, request, *args, **kwargs):
		House = self.get_House()
		House.entity = None
		House.save()
		view_name = "verification"
		return HttpResponseRedirect(reverse(view_name))




class ConnectVerificationView(HouseAccountMixin, FormView):
	template_name = 'houses/connect_verification.html'
	form_class = None
	success_url = '/dashboard'

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		House = self.get_House()
		profile = self.get_profile()

		if House.entity == "individual":
				context["business"] = False
		else:
			context["business"] = True

		context["profile"] = profile
		context["House"] = House
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		House = self.get_House()
		form = None

		if House.entity:
			if House.entity == "individual":
				self.form_class = ConnectIndividualVerificationForm
			else:
				self.form_class = ConnectCompanyVerificationForm
			form = self.get_form()

		else:
			self.template_name = "houses/select_entity.html"
			entity = False
		
		return self.render_to_response(self.get_context_data(form))


	def get_client_ip(self, request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip


	def form_valid(self, form, request, token):

		stripe.api_key = settings.STRIPE_SECRET_KEY
		House = self.get_House()

		# Form Field Variables
		business_name = form.cleaned_data.get("business_name")
		business_number = form.cleaned_data.get("business_number")
		email = form.cleaned_data.get("primary_email")
		first_name = form.cleaned_data.get("first_name")
		last_name = form.cleaned_data.get("last_name")
		city = form.cleaned_data.get("city")
		line_1 = form.cleaned_data.get("line_1")
		postal_code = form.cleaned_data.get("postal_code")
		state = form.cleaned_data.get("province")
		dob_day = form.cleaned_data.get("dob_day")
		dob_month = form.cleaned_data.get("dob_month")
		dob_year = form.cleaned_data.get("dob_year")
		personal_id_number = form.cleaned_data.get("personal_id_number")

		ip_address = self.get_client_ip(request)
		if not ip_address:
			ip_address = "70.50.85.53"


		# Stripe Account Creation
		stripe.api_key = settings.STRIPE_SECRET_KEY
		stripe_account = stripe.Account.create(country="CA", type="custom", email=email)

		# Save Stripe Account ID to House model
		House.connected_stripe_account_id = stripe_account.id
		house.save()

		# Add required fields to stripe account 
		stripe_account.tos_acceptance.date = int(time.time())
		stripe_account.tos_acceptance.ip = ip_address
		stripe_account.legal_entity.business_name = business_name
		stripe_account.legal_entity.business_tax_id = business_number
		stripe_account.legal_entity.type = "individual"
		stripe_account.legal_entity.first_name = first_name
		stripe_account.legal_entity.last_name = last_name
		stripe_account.legal_entity.personal_id_number = personal_id_number
		stripe_account.legal_entity.address.city = city
		stripe_account.legal_entity.address.line1 = line_1
		stripe_account.legal_entity.address.postal_code = postal_code
		stripe_account.legal_entity.address.state = state
		stripe_account.legal_entity.dob.day = dob_day
		stripe_account.legal_entity.dob.month = dob_month
		stripe_account.legal_entity.dob.year = dob_year

		try:
			stripe_account.save()
		except Exception as e:
			body = e.json_body
			err = body.get('error', {})
			print(err)
		

		front_side = form.cleaned_data.get("front_side_drivers_license")
		back_side = form.cleaned_data.get("back_side_drivers_license")

		print(form.cleaned_data)
		
		house.front_side = front_side
		house.back_side = back_side
		house.save()

		inImg1 = request.FILES["front_side_drivers_license"]
		inImg2 = request.FILES["back_side_drivers_license"]
		result = merge_images(inImg1, inImg2)
		w, h = result.size

		result = result.resize((int(w/3), int(h/3)))

		image_io = BytesIO()
		result.save(image_io, format='JPEG', quality=90)
		house.legal_document.save("legal_document.JPEG", ContentFile(image_io.getvalue()))
		house.save()


		# Stripe File Upload 
		from django.core.files.uploadedfile import SimpleUploadedFile
		print(house.legal_document.url)
		
		fp = SimpleUploadedFile(house.legal_document.url, house.legal_document.read())
		file_upload = stripe.FileUpload.create(purpose="identity_document", file=fp, stripe_account=stripe_account.id)

		house.stripe_legal_document_id = file_upload.id
		house.save()
		print(file_upload)

		stripe_account.legal_entity.verification.document = file_upload.id
		stripe_account.save()
		print(stripe_account)

		

		valid_data = super(ConnectVerificationView, self).form_valid(form)
		return valid_data


	def post(self, request, *args, **kwargs):
		data = request.POST
		house = self.get_house()

		if "Individual" in data:
			house.entity = "individual"
			house.save()
			return redirect('verification')
		elif "Company" in data:
			house.entity = "company"
			house.save()
			return redirect('verification')
		else:
			print(data)
			if house.entity == "individual":
				self.form_class = ConnectIndividualVerificationForm
			else:
				self.form_class = ConnectCompanyVerificationForm

			# stripe.api_key = settings.STRIPE_SECRET_KEY
			token = data["token"]
			# print(token)
			# stripe_account = stripe.Account.create(country="CA", type="custom", account_token=token)
			# house.connected_stripe_account_id = stripe_account.id
			# house.save()

			form = self.get_form()
			if form.is_valid():
				return self.form_valid(form, request, token)
			else:
				return self.form_invalid(form, request)

	def form_invalid(self, form, request):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



























