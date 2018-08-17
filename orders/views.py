import stripe
from django.conf import settings
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages

from organizations.mixins import OrganizationAccountMixin
from .models import EventOrder
from events.models import Event
from attendees.models import Attendee
from questions.models import EventQuestion

from .forms import RefundForm

# Create your views here.

class OrderListView(OrganizationAccountMixin, ListView):
	model = EventOrder
	template_name = "orders/event_orders.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def get_context_data(self, *args, **kwargs):
		context = {}
		organization = self.get_organization()
		event = self.get_event(self.kwargs['slug'])
		orders = EventOrder.objects.filter(event=event).order_by('created_at')
		print(orders)
		
		context["organization"] = organization
		context["orders"] = orders
		context["event"] = event
		return context



class OrderDetailView(OrganizationAccountMixin, FormView):
	model = EventOrder
	template_name = "orders/event_order_detail.html"

	def get_success_url(self):
		view_name = "events:orders:list"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_order(self, order_id):
		try:
			order = EventOrder.objects.get(pk=order_id)
			return order
		except Exception as e:
			print(e)
			raise Http404

	def get_context_data(self, event, order, request, form, *args, **kwargs):
		context = {}
		context["event"] = event
		context["order"] = order
		context["event_questions"] = EventQuestion.objects.filter(event=event, deleted=False, approved=True)
		context["attendees"] = Attendee.objects.filter(order=order)
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		context = {}
		slug = kwargs['slug']
		order_id = kwargs['pk']
		event = self.get_event(slug)
		order = self.get_order(order_id)
		form = RefundForm(total=order.amount)
		return self.render_to_response(self.get_context_data(event=event, request=request, order=order, form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		order_id = kwargs['pk']
		event = self.get_event(slug)
		order = self.get_order(order_id)

		form = RefundForm(total=order.amount, data=data)
		if form.is_valid():
			messages.success(request, 'Success!')
			return self.form_valid(form, request, event, order)
		else:
			messages.warning(request, 'Please try again.')
			return self.form_invalid(form, request, event, order)

	def form_valid(self, form, request, event, order):
		partial_refund = form.cleaned_data['partial_refund']
		refund_amount = form.cleaned_data['refund_amount']

		print(partial_refund)
		print(refund_amount)

		valid_data = super(OrderDetailView, self).form_valid(form)

	def form_invalid(self, form, request, event, order):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form, request=request, event=event, order=order))


















