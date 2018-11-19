import decimal
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib import messages

from organizations.mixins import OrganizationAccountMixin

from events.models import Event
from orders.models import EventOrder
from .models import EventPayout
from .forms import EventPayoutForm


# Create your views here.
class EventPayoutView(OrganizationAccountMixin, FormView):
	template_name = "payouts/event_payouts.html"

	def get_success_url(self):
		view_name = "events:payouts:event_payout"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})


	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404

	def get_orders(self, event):
		orders = EventOrder.objects.filter(event=event, failed=False, payout=None).order_by('created_at')
		return orders

	def get_context_data(self, form, event, request, *args, **kwargs):
		context = {}
		events = self.get_events()
		orders = self.get_orders(event)
		context["payout_amount"] = orders.aggregate(Sum('amount'))
		context["event"] = event
		context["orders"] = orders
		context["form"] = form
		context["events_tab"] = True
		context["events"] = events
		return context


	def get(self, request, *args, **kwargs):
		context = {}

		slug = kwargs['slug']
		event = self.get_event(slug)
		orders = self.get_orders(event)

		form = EventPayoutForm(orders=orders)
		return self.render_to_response(self.get_context_data(form=form, event=event, request=request))



	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		event = self.get_event(slug)
		orders = self.get_orders(event) 

		form = EventPayoutForm(orders=orders, data=data)
		
		if form.is_valid():
			messages.success(request, 'Payout Sent!')
			return self.form_valid(form, orders, request, event)
		else:
			messages.warning(request, 'Oops! Something went wrong.')
			return self.form_invalid(form, request, event)


	def form_valid(self, form, orders, request, event):

		event_payout = EventPayout.objects.create(event=event)
		event_payout.save()
		amount = decimal.Decimal(0.00)

		for order in orders:
			order_value = form.cleaned_data['%s_order' % (order.id)]
			if order_value == True:
				try:
					order.payout = event_payout
					amount = amount + order.amount
					order.save()
				except:
					pass
			else:
				pass

		event_payout.amount = amount
		event_payout.save()

		valid_data = super(EventPayoutView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form, request, event):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, request=request, event=event))















