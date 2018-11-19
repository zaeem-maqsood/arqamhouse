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

from .mixins import OrganizationAccountMixin, OrganizationLandingMixin

from django.contrib.auth.models import User
from profiles.models import Profile
from .models import Organization, OrganizationUser, SelectedUserOrganization
from .forms import OrganizationAndUserCreateForm, ConnectIndividualVerificationForm, ConnectCompanyVerificationForm

from events.models import Event
from tickets.models import Ticket
from orders.models import EventOrder
from attendees.models import Attendee
from carts.models import EventCart, EventCartItem

# Create your views here.

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



class ChangeEntityTypeView(OrganizationAccountMixin, View):

	def get(self, request, *args, **kwargs):
		organization = self.get_organization()
		organization.entity = None
		organization.save()
		view_name = "verification"
		return HttpResponseRedirect(reverse(view_name))




class ConnectVerificationView(OrganizationAccountMixin, FormView):
	template_name = 'organizations/connect_verification.html'
	form_class = None
	success_url = '/dashboard'

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		profile = self.get_profile()

		if organization.entity == "individual":
				context["business"] = False
		else:
			context["business"] = True

		context["profile"] = profile
		context["organization"] = organization
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		organization = self.get_organization()
		form = None

		if organization.entity:
			if organization.entity == "individual":
				self.form_class = ConnectIndividualVerificationForm
			else:
				self.form_class = ConnectCompanyVerificationForm
			form = self.get_form()

		else:
			self.template_name = "organizations/select_entity.html"
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
		organization = self.get_organization()

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

		# Save Stripe Account ID to Organization model
		organization.connected_stripe_account_id = stripe_account.id
		organization.save()

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
		
		organization.front_side = front_side
		organization.back_side = back_side
		organization.save()

		inImg1 = request.FILES["front_side_drivers_license"]
		inImg2 = request.FILES["back_side_drivers_license"]
		result = merge_images(inImg1, inImg2)
		w, h = result.size

		result = result.resize((int(w/3), int(h/3)))

		image_io = BytesIO()
		result.save(image_io, format='JPEG', quality=90)
		organization.legal_document.save("legal_document.JPEG", ContentFile(image_io.getvalue()))
		organization.save()


		# Stripe File Upload 
		from django.core.files.uploadedfile import SimpleUploadedFile
		print(organization.legal_document.url)
		
		fp = SimpleUploadedFile(organization.legal_document.url, organization.legal_document.read())
		file_upload = stripe.FileUpload.create(purpose="identity_document", file=fp, stripe_account=stripe_account.id)

		organization.stripe_legal_document_id = file_upload.id
		organization.save()
		print(file_upload)

		stripe_account.legal_entity.verification.document = file_upload.id
		stripe_account.save()
		print(stripe_account)

		

		valid_data = super(ConnectVerificationView, self).form_valid(form)
		return valid_data


	def post(self, request, *args, **kwargs):
		data = request.POST
		organization = self.get_organization()

		if "Individual" in data:
			organization.entity = "individual"
			organization.save()
			return redirect('verification')
		elif "Company" in data:
			organization.entity = "company"
			organization.save()
			return redirect('verification')
		else:
			print(data)
			if organization.entity == "individual":
				self.form_class = ConnectIndividualVerificationForm
			else:
				self.form_class = ConnectCompanyVerificationForm

			# stripe.api_key = settings.STRIPE_SECRET_KEY
			token = data["token"]
			# print(token)
			# stripe_account = stripe.Account.create(country="CA", type="custom", account_token=token)
			# organization.connected_stripe_account_id = stripe_account.id
			# organization.save()

			form = self.get_form()
			if form.is_valid():
				return self.form_valid(form, request, token)
			else:
				return self.form_invalid(form, request)

	def form_invalid(self, form, request):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



class DashboardView(OrganizationAccountMixin, DetailView):
	model = Organization
	template_name = "organizations/dashboard.html"

	def get_events(self, organization):
		events = Event.objects.active_events(organization=organization)
		return events

	def get_attendees(self, organization):
		now = datetime.today()
		fifteen_days_earlier = now - timedelta(days=15)
		attendees = Attendee.objects.filter(order__event__organization=organization, order__created_at__range=(fifteen_days_earlier, now)).select_related("order", "ticket", "order__event").prefetch_related("order", "ticket", "order__event")
		return attendees

	def get_actions(self, events):
		actions = {}

		# Get events that don't have tickets yet
		events_without_tickets = []
		for event in events:
			tickets = event.ticket_set.all().count()
			if tickets < 1:
				events_without_tickets.append(event)
		actions["events_without_tickets"] = events_without_tickets
		return actions


	def get_sales(self, attendees):
		day_label = []
		sales_label = []
		fifteen_days_sum = []
		fifteen_days_order_sum = []
		fifteen_days_tickets_sum = []
		use_large_scale = False
		today = datetime.today()
		for x in range(15):
			one_day_earlier = today - timedelta(days=x)
			attendees_for_day = attendees.filter(order__created_at__day=one_day_earlier.day)
			order_ids = set()
			sales_sum = decimal.Decimal(0.00)
			for attendee in attendees_for_day:
				if not int(attendee.order.id) in order_ids:
					order_ids.add(attendee.order.id)
					sales_sum += attendee.order.amount
					if sales_sum > 20:
						use_large_scale = True

			fifteen_days_tickets_sum.append(len(attendees_for_day))
			fifteen_days_order_sum.append(len(order_ids))
			sales_label.append("%.2f" % sales_sum)
			fifteen_days_sum.append(sales_sum)		
			day_label.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))

		sales_label = list(reversed(sales_label))
		day_label = list(reversed(day_label))

		data_set_dict = {"sales_label": sales_label, "day_label": day_label, "use_large_scale": use_large_scale, "fifteen_days_sum": fifteen_days_sum, "fifteen_days_order_sum": fifteen_days_order_sum, "fifteen_days_tickets_sum": fifteen_days_tickets_sum}
		return data_set_dict



	def get(self, request, *args, **kwargs):


		# Generate 2000 attendees
		# event = Event.objects.get(id=3)
		# ticket = Ticket.objects.get(id=4)
		# for x in range(100):
		# 	today = datetime.today()
		# 	random_date = today - timedelta(days=random.randint(0, 15))
		# 	event_cart = EventCart.objects.create(event=event, processed=True, total=52.80, stripe_charge=1.83)
		# 	event_cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1, paid_ticket=True, pass_fee=True, ticket_price=52.80, cart_item_total=52.80) 
		# 	order = EventOrder.objects.create(event=event, event_cart=event_cart, email="zaeem.maqsood@gmail.com", amount=52.80, payment_id="ch_1DS7mHHblWxAI5San4koFles", last_four="4242", brand="Visa", network_status="approved_by_network", risk_level="normal", seller_message="Payment complete.", outcome_type="authorized", name="Zaeem Maqsood", address_line_1="$7 Denny Street", address_state="ON", address_postal_code="L1Z0S3", address_city="Ajax", address_country="Canada")
		# 	attendee = Attendee.objects.create(order=order, ticket=ticket, name="Zaeem Maqsood")
		# 	attendee.created_at = random_date
		# 	order.created_at = random_date
		# 	order.save()
		# 	attendee.save()


		context = {}
		organization = self.get_organization()
		profile = self.get_profile()
		attendees = self.get_attendees(organization)
		events = self.get_events(organization)
		sales_data = self.get_sales(attendees)
		actions = self.get_actions(events)

		context["events"] = events
		context["actions"] = actions
		context["profile"] = profile
		context["organization"] = organization
		context["attendees"] = attendees[:5]
		context["data_set_dict"] = sales_data
		context["dashboard_tab"] = True
		context["fifteen_day_sales"] = sum(sales_data["fifteen_days_sum"])
		context["fifteen_days_order_sum"] = sum(sales_data["fifteen_days_order_sum"])
		context["fifteen_days_tickets_sum"] = sum(sales_data["fifteen_days_tickets_sum"])
		return render(request, self.template_name, context)



class OrganizationLandingView(OrganizationLandingMixin, DetailView):
	model = Organization
	template_name = "organizations/organization_landing.html"

	def get(self, request, *args, **kwargs):
		context = {}
		slug = self.kwargs['slug']
		organization = self.get_organization(slug)
		if not organization:
			raise Http404
		users = self.get_users(organization)
		print(users)
		profiles = self.get_profiles(users)

		context["profiles"] = profiles
		context["users"] = users
		context["organization"] = organization
		return render(request, self.template_name, context)



class OrganizationAndUserCreateView(CreateView):
	model = Organization
	form_class = OrganizationAndUserCreateForm
	template_name = "organizations/organization_detail.html"

	def get_success_url(self):
		view_name = "dashboard"
		return reverse(view_name)

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		if form.is_valid():
			messages.success(request, 'Organization Created!')
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		
		# Get email and password from the form
		email = form.cleaned_data.get("email")
		password = form.cleaned_data.get("password")
		users_name = form.cleaned_data.get("users_name")

		# Create a user with this email and password
		try:
			user = User.objects.create_user(email, email, password)
		except:
			form.add_error("email", "It seems this email is already in use, please use a different email if you are creating a new organization.")
			return self.render_to_response(self.get_context_data(form=form))

		# Save the organization
		self.object = form.save()

		# Authenticate user 
		user = authenticate(request, username=email, password=password)
		
		# Make sure user is authenticated, log them in or diplay 404 error
		if user is not None:
			login(request, user)
			messages.success(request, 'Logged in as %s' % (user.username))
		else:
			raise Http404

		# Create User Profile
		profile = Profile.objects.create(user=user, name=users_name)
		profile.save()

		# Create Organization User
		organization_user = OrganizationUser.objects.create(organization=self.object, user=user, role="admin")
		organization_user.save()

		# Create Selected User Organization
		selected_user_organization = SelectedUserOrganization.objects.create(organization=self.object, user=user)
		selected_user_organization.save()

		valid_data = super(OrganizationAndUserCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



















