from .base import *

import tempfile
import qrcode
import decimal
import stripe
from django.db.models import Sum
from houses.mixins import HouseAccountMixin
from houses.models import HouseUser
from events.models import Event, EventOrder, Attendee, EventOrderRefund, EventQuestion, EventCart, EventCartItem
from payments.models import Refund, HouseBalance
from questions.models import Question

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from weasyprint import HTML, CSS
from django.utils.html import strip_tags

	


class OrderListView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, ListView):
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
		print("It came to post")
		print(data)
		event = self.get_event(self.kwargs['slug'])
		all_orders = EventOrder.objects.filter(event=event).order_by('-created_at')
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
		orders = EventOrder.objects.filter(event=event).order_by('-created_at')
		print(orders)
		
		context["house"] = house
		context["orders"] = orders
		context["event"] = event
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context





class OrderPublicDetailView(DetailView):
	model = EventOrder
	template_name = "events/orders/event_order_detail_public.html"

	def get_order(self, order_id):
		try:
			order = EventOrder.objects.get(public_id=order_id)
			return order
		except Exception as e:
			print(e)
			raise Http404

	def view_tickets(self, event, order):

		# PDF Attachment
		pdf_context = {}
		pdf_context["order"] = order
		
		pdf_content = render_to_string('pdfs/ticket.html', pdf_context)
		pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))

		pdf_file = HTML(string=pdf_content).write_pdf(stylesheets=[pdf_css])

		response = HttpResponse(pdf_file, content_type='application/pdf;')
		response['Content-Disposition'] = 'inline; filename=confirmation.pdf'
		return response

	def get(self, request, *args, **kwargs):
		context = {}
		data = request.GET
		order_id = self.kwargs['public_id']
		order = self.get_order(order_id)
		event = order.event

		if 'view_tickets' in data:
			return self.view_tickets(event, order)

		attendees = Attendee.objects.filter(order=order)
		active_attendees = attendees.filter(active=True)
		context["active_attendees"] = active_attendees
		event_order_refunds = EventOrderRefund.objects.filter(order=order)
		if event_order_refunds:
			total_payout = event_order_refunds.aggregate(Sum('refund__amount'))
			total_payout = order.event_cart.total - \
				total_payout["refund__amount__sum"]
			if total_payout < 0.00:
				total_payout = 0.00
			total_payout = '{0:.2f}'.format(total_payout)
			context["total_payout"] = total_payout

		context["event_cart_items"] = order.event_cart.eventcartitem_set.all
		context["event"] = event
		context["order"] = order
		context["event_order_refunds"] = event_order_refunds
		context["attendees"] = attendees

		return render(request, self.template_name, context)





class OrderDetailView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, FormView):
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
			order = EventOrder.objects.get(public_id=order_id)
			return order
		except Exception as e:
			print(e)
			raise Http404

	def get_context_data(self, *args, **kwargs):
		context = {}

		slug = self.kwargs['slug']
		order_id = self.kwargs['public_id']
		event = self.get_event(slug)
		order = self.get_order(order_id)
		house = self.get_house()
		house_users = HouseUser.objects.filter(house=event.house, profile__is_superuser=False)

		print("house users")
		print(house_users)

		house_balance = HouseBalance.objects.get(house=house)
		attendees = Attendee.objects.filter(order=order)
		active_attendees = attendees.filter(active=True)
		context["active_attendees"] = active_attendees
		event_order_refunds = EventOrderRefund.objects.filter(order=order)
		if event_order_refunds:
			total_payout = event_order_refunds.aggregate(Sum('refund__house_amount'))
			total_payout = order.event_cart.total_no_fee - total_payout["refund__house_amount__sum"]
			if total_payout < 0.00:
				total_payout = 0.00
			total_payout = '{0:.2f}'.format(total_payout)
			context["total_payout"] = total_payout

		context["house_balance"] = house_balance
		context["event_cart_items"] = order.event_cart.eventcartitem_set.all
		context["house"] = house
		context["event"] = event
		context["order"] = order
		context["event_order_refunds"] = event_order_refunds
		context["attendees"] = attendees
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

	def get(self, request, *args, **kwargs):
		return self.render_to_response(self.get_context_data())


	def send_refund_confirmation_email(self, order):
		
		# PDF Attachment
		pdf_context = {}
		event_order_refunds = EventOrderRefund.objects.filter(order=order)
		pdf_context["event_order_refunds"] = event_order_refunds
		if event_order_refunds:
			total_payout = event_order_refunds.aggregate(Sum('refund__amount'))
			total_payout = order.event_cart.total - total_payout["refund__amount__sum"]
			if total_payout < 0.00:
				total_payout = 0.00
			total_payout = '{0:.2f}'.format(total_payout)
			pdf_context["total_payout"] = total_payout
		
		pdf_context["order"] = order
		pdf_content = render_to_string('pdfs/refund_summary.html', pdf_context)
		pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))
		pdf_file = HTML(string=pdf_content).write_pdf(stylesheets=[pdf_css])

		# Compose Email
		subject = 'Order Refund For %s' % (order.event.title)
		context = {}
		context["event"] = order.event
		context["order"] = order
		html_content = render_to_string('emails/order_refund.html', context)
		text_content = strip_tags(html_content)
		from_email = 'Order Refund <info@arqamhouse.com>'
		to = ['%s' % (order.email)]
		email = EmailMultiAlternatives(subject=subject, body=text_content,
		                               from_email=from_email, to=to)
		email.attach_alternative(html_content, "text/html")
		email.attach("updated_confirmation.pdf", pdf_file, 'application/pdf')
		email.send()
		return "Done"


	def view_tickets(self, event, order):

		# PDF Attachment
		pdf_context = {}
		pdf_context["order"] = order
		pdf_content = render_to_string('pdfs/ticket.html', pdf_context)
		pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))
		

		# Creating http response
		response = HttpResponse(content_type='application/pdf;')
		response['Content-Disposition'] = 'inline; filename=list_people.pdf'

		pdf_file = HTML(string=pdf_content).write_pdf(response, stylesheets=[pdf_css])
		return response



	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)
		slug = kwargs['slug']
		order_id = kwargs['public_id']
		event = self.get_event(slug)
		order = self.get_order(order_id)
		attendees = Attendee.objects.filter(order=order)

		if 'view_tickets' in data:
			return self.view_tickets(event, order)


		if 'Refund' in data:

			attendee_to_be_refunded_id = data['Refund']
			attendee_to_be_refunded = attendees.get(id=attendee_to_be_refunded_id)
			ticket = attendee_to_be_refunded.ticket
			amount = int(attendee_to_be_refunded.ticket_buyer_price * 100)
			house_amount = int(attendee_to_be_refunded.ticket_price * 100)

			house = self.get_house()
			house_balance = HouseBalance.objects.get(house=house)
			house_balance.balance -= attendee_to_be_refunded.ticket_fee
			house_balance.save()

			if attendees.filter(active=True).count() == 1:
				partial_refund = False
				full_refund = True
			else:
				partial_refund = True
				full_refund = False

			if attendee_to_be_refunded.active:
				event_order_refund = EventOrderRefund.objects.create(order=order, attendee=attendee_to_be_refunded)
				refund = Refund.objects.create(transaction=order.transaction, amount=(
					amount/100), house_amount=(house_amount/100), partial_refund=partial_refund)
				
				event_order_refund.refund = refund
				event_order_refund.save()
				
				attendee_to_be_refunded.active = False
				attendee_to_be_refunded.save()
				attendee_to_be_refunded.ticket.amount_sold -= 1
				attendee_to_be_refunded.ticket.sold_out = False
				attendee_to_be_refunded.ticket.save()
				
				order.partial_refund = partial_refund
				order.refunded = full_refund
				order.save()

				stripe.api_key = settings.STRIPE_SECRET_KEY
				response = stripe.Refund.create(charge=order.transaction.payment_id, amount=amount)
			
			# Send Confirmation Email
			self.send_refund_confirmation_email(order)



		# User wants a full refund on the order
		if 'Full Refund' in data:

			for attendee in attendees:
				if attendee.active:
					amount = int(attendee.ticket_buyer_price * 100)
					house_amount = int(attendee.ticket_price * 100)
					event_order_refund = EventOrderRefund.objects.create(order=order, attendee=attendee)
					refund = Refund.objects.create(
						transaction=order.transaction, amount=(amount/100), house_amount=(house_amount/100))
					event_order_refund.refund = refund
					event_order_refund.save()
					attendee.active = False
					attendee.save()
					attendee.ticket.amount_sold -= 1
					attendee.ticket.sold_out = False
					attendee.ticket.save()
					stripe.api_key = settings.STRIPE_SECRET_KEY
					response = stripe.Refund.create(charge=order.transaction.payment_id, amount=amount)

				order.refunded = True
				order.save()

			# Send Confirmation email
			self.send_refund_confirmation_email(order)


		return render(request, self.template_name, self.get_context_data(data))






