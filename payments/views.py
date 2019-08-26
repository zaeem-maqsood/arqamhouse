from django.shortcuts import render
import decimal
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib import messages


from houses.mixins import HouseAccountMixin
from .models import Payout


# Create your views here.
class PayoutDetailView(HouseAccountMixin, DetailView):
	template_name = "payouts/detail.html"
	model = Payout

	def get_context_data(self, *args, **kwargs):
		context = {}
		payout = kwargs['object']
		house = self.get_House()
		events = self.get_events()
		context["payout"] = payout
		context["house"] = house
		context["events"] = events
		context["payout_history"] = True
		return context


class PayoutHistoryView(HouseAccountMixin, ListView):
	template_name = "payouts/history.html"
	model = Payout

	def payouts_total(self, payouts):
		total = payouts.aggregate(Sum('amount'))
		return total['amount__sum']

	def get_payouts(self, House):
		payouts = Payout.objects.filter(House=House)
		return payouts

	def get_context_data(self, *args, **kwargs):
		context = {}
		House = self.get_House()
		payouts = self.get_payouts(House)
		payouts_total = self.payouts_total(payouts)
		events = self.get_events()
		context["House"] = House
		context["events"] = events
		context["payouts_total"] = payouts_total
		context["payouts"] = payouts
		context["payout_history"] = True
		return context