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
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseRedirect

from .mixins import HouseAccountMixin, HouseLandingMixin

from django.contrib.auth.models import User
from profiles.models import Profile
from .models import House, HouseUser
from .forms import HouseForm, ConnectIndividualVerificationForm, ConnectCompanyVerificationForm

from events.models import Event, Ticket, EventCart, EventCartItem, EventOrder, Attendee
from profiles.models import Profile



# Create your views here.



class DashboardView(HouseAccountMixin, DetailView):
	model = House
	template_name = "houses/new_dashboard.html"


	def get_attendees(self, house):
		now = datetime.today()
		ten_days_earlier = now - timedelta(days=10)
		attendees = Attendee.objects.filter(order__event__house=house, order__created_at__range=(ten_days_earlier, now)).select_related("order", "ticket", "order__event").prefetch_related("order", "ticket", "order__event")
		return attendees

	def get_10_day_orders(self, house):
		data = {}
		today = datetime.today()
		ten_days_earlier = today - timedelta(days=10)

		all_orders = EventOrder.objects.filter(event__house=house ,created_at__lte=today, created_at__gte=ten_days_earlier)
		data_sales = []
		data_days = []
		use_large_scale = False
		for x in range(11):
			one_day_earlier = today - timedelta(days=x)
			data_days.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))
			orders = all_orders.filter(created_at__day=one_day_earlier.day)
			today_sum = orders.aggregate(Sum('amount'))
			if today_sum["amount__sum"] == None:
				data_sales.append(0.00)
			else:
				data_sales.append(float(today_sum['amount__sum']))
				if today_sum["amount__sum"] > 20:
					use_large_scale = True
		data_total_orders = all_orders.count()
		data_total_sales = sum(data_sales)
		data["data_sales"] = list(reversed(data_sales))
		data["data_days"] = list(reversed(data_days))
		data["data_total_orders"] = data_total_orders
		data["data_total_sales"] = data_total_sales
		data["use_large_scale"] = use_large_scale
		return data



	def get(self, request, *args, **kwargs):

		context = {}

		# ------------- House Mixin Context Variables 
		house = self.get_house()
		events = self.get_events()
		profile = self.get_profile()
		context["house"] = house
		context["dashboard_events"] = events
		context["profile"] = profile
		# ------------- House Mixin Context Variables 

		attendees = self.get_attendees(house)
		context["attendees"] = attendees[:5]
		# context["data"] = self.get_10_day_orders(house)
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






class HouseCreateView(CreateView):
	model = House
	template_name = "houses/house_create.html"

	def get_success_url(self):
		view_name = "houses:dashboard"
		return reverse(view_name, kwargs={'slug': self.object.slug})

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
		house_user = HouseUser.objects.create(house=self.object, profile=profile, role="admin")
		house_user.save()

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



























