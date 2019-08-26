from .base import *

import qrcode
import decimal
import stripe
from houses.mixins import HouseAccountMixin
from events.models import Event, EventOrder, Attendee, EventQuestion
from questions.models import Question

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from weasyprint import HTML, CSS



class OrderListView(HouseAccountMixin, ListView):
	model = EventOrder
	template_name = "events/orders/event_orders.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)
		event = self.get_event(self.kwargs['slug'])
		all_orders = EventOrder.objects.filter(event=event).order_by('created_at')
		search_terms = data["search"].split()

		if data["search"] == '':
			orders = all_orders
		else:
			counter = 0
			for search_term in search_terms:
				if counter == 0:
					orders = all_orders.filter(Q(name__icontains=search_term) | Q(transaction__amount__icontains=search_term))
				else:
					orders = orders.filter(Q(name__icontains=search_term) | Q(transaction__amount__icontains=search_term))
				print(counter)
				counter += 1
		
		orders = orders[:100]
		print(orders)
		html = render_to_string('events/orders/orders-dynamic-table-body.html', {'orders': orders, 'request':request})
		return HttpResponse(html)

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		event = self.get_event(self.kwargs['slug'])
		orders = EventOrder.objects.filter(event=event).order_by('created_at')
		print(orders)
		
		context["house"] = house
		context["orders"] = orders
		context["event"] = event
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context



class OrderDetailView(HouseAccountMixin, FormView):
	model = EventOrder
	template_name = "events/orders/event_order_detail.html"

	def get_success_url(self):
		view_name = "events:order_list"
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

	def get_context_data(self, *args, **kwargs):
		context = {}

		slug = self.kwargs['slug']
		order_id = self.kwargs['pk']
		event = self.get_event(slug)
		order = self.get_order(order_id)
		house = self.get_house()
		attendees = Attendee.objects.filter(order=order)


		# Testing ------------------------------------------------------------------------------------------------
		# send_mail('subject', 'body of the message', 'info@arqamhouse.com', ['zaeem@arqamhouse.com'])

		# order.qrcode()
		# context_dict = {}
		# context_dict["order"] = order
		# html_string = render_to_string('pdfs/ticket.html', context_dict)
		# css_string = render_to_string('pdfs/ticket.css')
		# html = HTML(string=html_string)
		# css_styles = CSS(string=css_string)
		# css_bootstrap = CSS(url="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css")
		# order.pdf = SimpleUploadedFile(order.name +'.pdf', html.write_pdf(stylesheets=[css_bootstrap, css_styles]), content_type='application/pdf')
		# order.save()
		# Testing ------------------------------------------------------------------------------------------------

		context["event_cart_items"] = order.event_cart.eventcartitem_set.all
		context["house"] = house
		context["event"] = event
		context["order"] = order
		context["attendees"] = attendees
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):

		

		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		order_id = kwargs['pk']
		event = self.get_event(slug)
		order = self.get_order(order_id)

		if 'Partial Refund' in data:
			print(data)

			amount = int(data['partial']) * 100
			print(amount)
			stripe.api_key = settings.STRIPE_SECRET_KEY
			
			try:

				refund = stripe.Refund.create(
					charge=order.transaction.payment_id,
					amount=amount,
				)

				order.refunded = True
				order.transaction.refunded = True
				order.transaction.save()
				order.save()

			except Exception as e:
				print(e)


			# return HttpResponseRedirect(self.get_success_url())

		return render(request, self.template_name, self.get_context_data(data))






