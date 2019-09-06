from django.shortcuts import render
import decimal
import stripe 
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib import messages
from itertools import chain
from operator import attrgetter
from django.conf import settings
from django.http import Http404, HttpResponseRedirect

from houses.mixins import HouseAccountMixin
from .models import Payout, Transaction, Refund, HousePayment
from .forms import AddFundsForm, PayoutForm


# Create your views here.

class PayoutView(HouseAccountMixin, FormView):
	template_name = "payments/payout.html"
	form_class = PayoutForm
	model = Payout

	def get_success_url(self):
		view_name = "payments:list"
		return reverse(view_name)

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		transactions = Transaction.objects.filter(house=house)
		refunds = Refund.objects.filter(transaction__in=transactions)

		transactions_amount = transactions.aggregate(Sum('house_amount'))
		refunds_amount = refunds.aggregate(Sum('amount'))
		print(transactions_amount)
		print(refunds_amount)

		total = transactions_amount["house_amount__sum"] - refunds_amount["amount__sum"]
		total = '{0:.2f}'.format(total)
		print(total)
		form = self.get_form()
		context["form"] = form
		context["total"] = total
		context["dashboard_events"] = self.get_events()
		return context




class PaymentListView(HouseAccountMixin, View):
	
	template_name = "payments/list.html"

	def get_transactions(self, house):
		transactions = Transaction.objects.filter(house=house).order_by("-created_at")
		return transactions

	def get_refunds(self, house):
		refunds = Refund.objects.filter(transaction__house=house).order_by("-created_at")
		return refunds

	def get_payouts(self, house):
		payouts = Payout.objects.filter(house=house).order_by("-created_at")
		return payouts

	def get_payments(self, house):
		transactions = self.get_transactions(house)
		refunds = self.get_refunds(house)
		payouts = self.get_payouts(house)
		payments = sorted(chain(transactions, refunds, payouts), key=attrgetter('created_at'), reverse=True)
		return payments


	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def get_context_data(self, data=None, *args, **kwargs):
		context = {}
		house = self.get_house()
		payments = self.get_payments(house)
		context["payments"] = payments
		context["dashboard_events"] = self.get_events()
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
			transaction = Transaction.objects.create(house=house)
			charge = stripe.Charge.create(
							amount = stripe_charge_amount,
							currency = 'cad',
							description = 'Funds added for %s' % (house.name),
							source = stripe_token,
							statement_descriptor = 'Arqam House Inc.',
						)
			print(charge)

			transaction.amount = amount
			transaction.house_amount = house_total
			transaction.stripe_amount = stripe_amount
			transaction.arqam_amount = arqam_amount

			transaction.payment_id = charge['id']
			transaction.failure_code = charge['failure_code']
			transaction.failure_message = charge['failure_message']
			transaction.last_four = charge.source['last4']
			transaction.brand = charge.source['brand']
			transaction.network_status = charge.outcome['network_status']
			transaction.reason = charge.outcome['reason']
			transaction.risk_level = charge.outcome['risk_level']
			transaction.seller_message = charge.outcome['seller_message']
			transaction.outcome_type = charge.outcome['type']
			transaction.email = user.email
			transaction.name = charge.source['name']
			transaction.address_line_1 = charge.source['address_line1']
			transaction.address_state = charge.source['address_state']
			transaction.address_postal_code = charge.source['address_zip']
			transaction.address_city = charge.source['address_city']
			transaction.address_country = charge.source['address_country']
			transaction.save()
			house_payment = HousePayment.objects.create(transaction=transaction)
			house_payment.save()
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


