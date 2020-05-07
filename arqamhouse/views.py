from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

from .forms import ReportErrorForm

class ApplePayVerificationView(TemplateView):
	template_name = 'static/apple-developer-merchantid-domain-association'


class CustomScriptView(View):
	template_name = "frontend/custom_script.html"

	def get(self, request, *args, **kwargs):
		context = {}

		import decimal
		from django.db.models import Max, Sum, Avg
		from houses.models import House
		from events.models import Event, EventOrder
		from donations.models import Donation, DonationType
		from subscribers.models import Subscriber, Campaign, Audience

		# # 1. Resave all houses with updated values
		houses = House.objects.all()
		# for house in houses:
		# 	donations = Donation.objects.filter(donation_type__house=house)
		# 	house.donation_score = 0
		# 	house.donation_amount_score = decimal.Decimal('0.00')
		# 	house.save()


		# # 2. Update Subscribers
		# subscribers = Subscriber.objects.all()
		# for subscriber in subscribers:

		# 	events = Event.objects.filter(house=house, deleted=False)
		# 	subscriber.total_events_since_subscribed = events.count()

		# 	# Event attendance
		# 	event_orders = EventOrder.objects.filter(event__house=subscriber.house).values('event').distinct()
		# 	subscriber.event_attendance = event_orders.count()

		# 	# campaigns
		# 	campaigns = subscriber.subscribers_sent_to.all()
		# 	campaigns_viewed = subscriber.subscribers_seen.all()

		# 	subscriber.total_campaigns_since_subscribed = campaigns.count()
		# 	subscriber.campaign_views = campaigns_viewed.count()

		# 	# donation amount
		# 	donations = Donation.objects.filter(donation_type__house=subscriber.house, email=subscriber.profile.email)
		# 	subscriber.times_donated = donations.count()


		# 	# donation amount
		# 	donation_amount = donations.aggregate(Sum('transaction__amount'))["transaction__amount__sum"]
		# 	if donation_amount is None:
		# 		donation_amount = decimal.Decimal('0.00')

		# 	subscriber.amount_donated = donation_amount

		# 	subscriber.save()

		
		# # 3. Update House 
		# for house in houses:
		# 	# Aggregate the avg amount of times people have donated
		# 	subscribers = Subscriber.objects.filter(house=house)
		# 	time_donated_average = subscribers.aggregate(Avg('times_donated'))["times_donated__avg"]
		# 	house.donation_score = time_donated_average

		# 	# Aggregate the avg amount people have donated
		# 	donations = Donation.objects.filter(donation_type__house=house)
		# 	average_donation_amount = donations.aggregate(Avg('transaction__amount'))["transaction__amount__avg"]
		# 	if average_donation_amount is None:
		# 		average_donation_amount = decimal.Decimal('0.00')
		# 	house.donation_amount_score = average_donation_amount
			
		# 	# Save the global house values
		# 	house.save()


		# # 4. Updates all campaigns 
		# campaigns = Campaign.objects.all()
		# for campaign in campaigns:
		# 	campaign.save()


		# 5. Create audiences
		for house in houses:
			events = Event.objects.filter(house=house)
			for event in events:
				try:
					audience = Audience.objects.get(house=house, event=event)
				except Exception as e:
					print(e)
					audience = Audience.objects.create(house=house, name=f"{event.title} audience", event=event)
					event_orders = EventOrder.objects.filter(event=event)
					for event_order in event_orders:
						try:
							subscriber = Subscriber.objects.get(profile__email=event_order.email, house=house)
							audience.subscribers.add(subscriber)
						except Exception as e:
							print(e)

			donation_types = DonationType.objects.filter(house=house)
			for donation_type in donation_types:
				try:
					audience = Audience.objects.get(house=house, donation_type=donation_type)
				except Exception as e:
					print(e)
					audience = Audience.objects.create(house=house, name=f"{donation_type.name} audience", donation_type=donation_type)
					donations = Donation.objects.filter(donation_type=donation_type)
					for donation in donations:
						try:
							subscriber = Subscriber.objects.get(profile__email=donation.email, house=house)
							audience.subscribers.add(subscriber)
						except Exception as e:
							print(e)


		return render(request, self.template_name, context)


class HomePageView(View):
	template_name = "frontend/home.html"

	def get_house(self):
		profile = self.request.user
		house = profile.house
		return house

	def get(self, request, *args, **kwargs):
		context = {}
		try:
			house = self.get_house()
			response = redirect('profile/login')
			return response
		except:
			return render(request, self.template_name, context)



class AboutUsView(View):
	template_name = "frontend/about.html"

	def get_house(self):
		profile = self.request.user
		house = profile.house
		return house

	def get(self, request, *args, **kwargs):
		context = {}
		try:
			house = self.get_house()
			response = redirect('profile/login')
			return response
		except:
			return render(request, self.template_name, context)



class PricingView(View):
	template_name = "frontend/pricing.html"

	def get(self, request, *args, **kwargs):
		context = {}
		return render(request, self.template_name, context)



class ReportErrorView(FormView):

	template_name = "static/report_error.html"
	success_url = "/report"

	def get(self, request, *args, **kwargs):
		context = {}
		profile = request.user
		context["profile"] = profile
		form = ReportErrorForm()
		context["form"] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)
		form = ReportErrorForm(data=data)
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
		self.send_payout_email(name, message)
		messages.success(request, 'Message Sent!')
		valid_data = super(ReportErrorView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


	def send_payout_email(self, name, message):
		subject = 'New Error Report'
		context = {}
		context["name"] = name
		context["message"] = message
		html_message = render_to_string('emails/error_report.html', context)
		plain_message = strip_tags(html_message)
		from_email = 'Error Manager <admin@arqamhouse.com>'
		to = ['errors@arqamhouse.com']
		mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
		return "Done"
