from django.shortcuts import render
import decimal
import stripe 
import datetime
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib import messages
from itertools import chain
from operator import attrgetter
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import timezone

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from houses.mixins import HouseAccountMixin
from houses.models import HouseUser
from .models import Payout, Transaction, Refund, HousePayment, HouseBalance, HouseBalanceLog, PayoutSetting, BankTransfer
from .forms import AddFundsForm, PayoutForm, AddBankTransferForm


# Create your views here.
class UpdateBankTransferView(HouseAccountMixin, CreateView):
	template_name = "payments/add_bank.html"
	form_class = AddBankTransferForm
	model = PayoutSetting

	def get_success_url(self):
		view_name = "payments:payout_settings_list"
		return reverse(view_name)

	def get(self, request, *args, **kwargs):
		data = request.GET
		print(data)
		if 'institution_number' in data:
				try:
					return render(request, "payments/bank_images/%s.html" % (data["institution_number"]))
				except Exception as e:
					print(e)
					return HttpResponse("")
		bank_transfer_id = kwargs['bank_transfer_id']
		self.object = BankTransfer.objects.get(id=bank_transfer_id)
		return render(request, self.template_name, self.get_context_data())

	
	def post(self, request, *args, **kwargs):
		bank_transfer_id = kwargs['bank_transfer_id']
		self.object = BankTransfer.objects.get(id=bank_transfer_id)
		data = request.POST
		house = self.get_house()
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request, data)
		else:
			return self.form_invalid(form)
	
	def form_valid(self, form, request, data):
		house = self.get_house()
		self.object = form.save()
		payout_method_name = request.POST["payout_method_name"]
		payout_setting = PayoutSetting.objects.get(house=house, bank_transfer=self.object)
		payout_setting.name = payout_method_name
		payout_setting.save()
		messages.success(request, 'Bank Account Updated!')
		valid_data = super(UpdateBankTransferView, self).form_valid(form)
		return valid_data

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		form = self.get_form()
		payout_setting = PayoutSetting.objects.get(house=house, bank_transfer=self.object)
		context["form"] = form
		context["payout_setting"] = payout_setting
		context["dashboard_events"] = self.get_events()
		context["house"] = self.get_house()
		context["update"] = True
		return context


	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



class AddBankTransferView(HouseAccountMixin, CreateView):
	template_name = "payments/add_bank.html"
	form_class = AddBankTransferForm
	model = PayoutSetting

	def get_success_url(self):
		view_name = "payments:payout_settings_list"
		return reverse(view_name)

	def get(self, request, *args, **kwargs):

		data = request.GET
		print(data)
		if 'institution_number' in data:
				try:
					return render(request, "payments/bank_images/%s.html" % (data["institution_number"]))
				except Exception as e:
					print(e)
					return HttpResponse("")
		self.object = None
		return render(request, self.template_name, self.get_context_data())

	
	def post(self, request, *args, **kwargs):
		data = request.POST
		house = self.get_house()
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)
	
	def form_valid(self, form, request):
		house = self.get_house()
		self.object = form.save()
		payout_method_name = request.POST["payout_method_name"]
		payout_setting = PayoutSetting.objects.create(house=house, bank_transfer=self.object, name=payout_method_name)
		messages.success(request, 'Payout Method Created!')
		valid_data = super(AddBankTransferView, self).form_valid(form)
		return valid_data

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		form = self.get_form()
		context["form"] = form
		context["dashboard_events"] = self.get_events()
		context["house"] = self.get_house()
		return context


	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))



class PayoutSettingsListView(HouseAccountMixin, View):
	template_name = "payments/payout_settings_list.html"

	def get_payout_settings(self, house):
		payout_settings = PayoutSetting.objects.filter(house=house)
		return payout_settings

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def get_context_data(self, data=None, *args, **kwargs):
		context = {}
		house = self.get_house()
		payout_settings = self.get_payout_settings(house)
		context["payout_settings"] = payout_settings
		context["dashboard_events"] = self.get_events()
		context["house"] = self.get_house()
		return context




class PayoutView(HouseAccountMixin, FormView):
	template_name = "payments/payout.html"
	model = Payout

	def get_success_url(self):
		view_name = "payments:list"
		return reverse(view_name)

	def get(self, request, *args, **kwargs):

		stripe.api_key = 'sk_live_4FvrAHAiKVjvUYouYDUAuT63'
		balance = stripe.Balance.retrieve()
		print(balance)
		return render(request, self.template_name, self.get_context_data())

	
	def post(self, request, *args, **kwargs):
		data = request.POST
		house = self.get_house()
		house_balance = HouseBalance.objects.get(house=house)
		form = PayoutForm(data=data, total=house_balance.balance, house=house)
		if form.is_valid():
			return self.form_valid(form, request, house_balance)
		else:
			return self.form_invalid(form)


	def send_payout_email_us(self, payout):
		subject = 'New payout for %s' % (payout.house.name)
		context = {}
		context["payout"] = payout
		context["house"] = payout.house
		context["payout_amount"] = '{0:.2f}'.format(payout.amount)
		html_message = render_to_string('emails/payout_notify_us.html', context)
		plain_message = strip_tags(html_message)
		from_email = 'Arqam House Payout <admin@arqamhouse.com>'
		to = ['info@arqamhouse.com', 'admin@arqamhouse.com']
		mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
		return "Done"

	def send_payout_email_them(self, payout):

		house_users = HouseUser.objects.filter(house=payout.house)
		print(house_users)
		emails = []
		for house_user in house_users:
			emails.append(str(house_user.profile.email))
			print("Email sent to %s" % (house_user.profile.email))
		subject = 'New payout for %s' % (payout.house.name)
		context = {}
		context["payout"] = payout
		context["house"] = payout.house
		context["payout_amount"] = '{0:.2f}'.format(payout.amount)
		html_message = render_to_string('emails/payout_notify_them.html', context)
		plain_message = strip_tags(html_message)
		from_email = 'Payout Information <info@arqamhouse.com>'
		to = emails
		mail.send_mail(subject, plain_message, from_email,
		               to, html_message=html_message, fail_silently=False)
		return "Done"

	
	def form_valid(self, form, request, house_balance):
		house = self.get_house()
		amount = decimal.Decimal(form.cleaned_data["amount"])
		payout_setting = form.cleaned_data["payout_setting"]
		payout = Payout.objects.create(house=house, amount=amount, payout_setting=payout_setting)
		self.send_payout_email_us(payout)
		self.send_payout_email_them(payout)
		messages.success(request, 'Payout Requested!')
		valid_data = super(PayoutView, self).form_valid(form)
		return valid_data



	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		house_balance = HouseBalance.objects.get(house=house)
		payout_settings = PayoutSetting.objects.filter(house=house)

		total = '{0:.2f}'.format(house_balance.balance)

		form = PayoutForm(house_balance.balance, house)
		context["form"] = form
		context["payout_settings"] = payout_settings
		context["house_balance"] = house_balance
		context["total"] = total
		context["dashboard_events"] = self.get_events()
		context["house"] = self.get_house()
		return context


	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))




class PaymentListView(HouseAccountMixin, View):
	template_name = "payments/list.html"

	def get_house_balance_logs(self, house_balance):
		house_balance_logs = HouseBalanceLog.objects.filter(house_balance=house_balance).order_by("-created_at")
		return house_balance_logs

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)
		house = self.get_house()
		house_balance = HouseBalance.objects.get(house=house)
		house_balance_logs = self.get_house_balance_logs(house_balance)

		if not data['reset'] == 'reset':

			start = data["start"]
			end = data["end"]

			log_type = data["log_type"]
			print(log_type)

			if start and end:
				today = timezone.now()
				start_year = int(start[0:4])
				end_year = int(end[0:4])

				start_month = int(start[5:7])
				end_month = int(end[5:7])

				start_day = int(start[8:10])
				end_day = int(end[8:10])
				print(start_day)
				print(end_day)

				house_balance_logs = house_balance_logs.filter(created_at__gte=datetime.date(start_year, start_month, start_day), created_at__lte=datetime.date(end_year, end_month, end_day))

			if log_type:
				if log_type == 'transaction':
					house_balance_logs = house_balance_logs.filter(transaction__isnull=False)
				elif log_type == 'refund':
					house_balance_logs = house_balance_logs.filter(refund__isnull=False)
				elif log_type == 'payout':
					house_balance_logs = house_balance_logs.filter(payout__isnull=False)
				elif log_type == 'house_payment':
					house_balance_logs = house_balance_logs.filter(house_payment__isnull=False)
				else:
					house_balance_logs = house_balance_logs


		html = render_to_string('payments/house_balance_logs_dynamic_table_body.html', {'house_balance_logs': house_balance_logs, 'request': request})
		return HttpResponse(html)


	def get_context_data(self, data=None, *args, **kwargs):
		context = {}
		house = self.get_house()
		house_balance = HouseBalance.objects.get(house=house)
		house_balance_logs = self.get_house_balance_logs(house_balance)
		context["house_balance"] = house_balance
		context["house_balance_logs"] = house_balance_logs
		context["dashboard_events"] = self.get_events()
		context["house"] = self.get_house()
		return context



class AddFundsView(HouseAccountMixin, FormView):
	template_name = "payments/add_funds.html"
	form_class = AddFundsForm
	model = Transaction

	def get_success_url(self):
		view_name = "payments:list"
		return reverse(view_name)

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}
		form = self.get_form()
		context["public_key"] = settings.STRIPE_PUBLIC_KEY
		context["form"] = form
		context["house"] = self.get_house()
		context["dashboard_events"] = self.get_events()
		return context

	
	def post(self, request, *args, **kwargs):
		data = request.POST
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)


	def form_valid(self, form, request):
		data = request.POST
		house = self.get_house()
		user = request.user
		print(data)
		stripe_token = data["stripeToken"]
		amount = decimal.Decimal(form.cleaned_data["amount"])

		stripe_charge_amount = amount * 100
		stripe_charge_amount = int(stripe_charge_amount)

		fee = (amount * decimal.Decimal(0.04)) + decimal.Decimal(0.30)
		stripe_amount = (amount * decimal.Decimal(0.029)) + decimal.Decimal(0.30)
		arqam_amount = fee - stripe_amount
		house_total = amount - fee
		
		try:
			stripe.api_key = settings.STRIPE_SECRET_KEY
			
			charge = stripe.Charge.create(
							amount = stripe_charge_amount,
							currency = 'cad',
							description = 'Funds added for %s' % (house.name),
							source = stripe_token,
							statement_descriptor = 'Arqam House Inc.',
						)
			print(charge)

			transaction = Transaction.objects.create(house=house,
			amount = amount,
			house_amount = house_total,
			stripe_amount = stripe_amount,
			arqam_amount = arqam_amount,
			house_payment = True,
			payment_id = charge['id'],
			failure_code = charge['failure_code'],
			failure_message = charge['failure_message'],
			last_four = charge.source['last4'],
			brand = charge.source['brand'],
			network_status = charge.outcome['network_status'],
			reason = charge.outcome['reason'],
			risk_level = charge.outcome['risk_level'],
			seller_message = charge.outcome['seller_message'],
			outcome_type = charge.outcome['type'],
			email = user.email,
			name = charge.source['name'],
			address_line_1 = charge.source['address_line1'],
			address_state = charge.source['address_state'],
			address_postal_code = charge.source['address_zip'],
			address_city = charge.source['address_city'],
			address_country = charge.source['address_country'],
			)
			house_payment = HousePayment.objects.create(transaction=transaction)
		except Exception as e:
			print(e)
			messages.success(request, 'An Error Occured. Please contact support.')
			return HttpResponseRedirect(self.get_success_url())
		

		messages.success(request, 'Funds Added!')
		valid_data = super(AddFundsView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


