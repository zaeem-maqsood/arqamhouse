from .base import *

from events.models import Event, Ticket, EventCart, EventCartItem
from events.forms import TicketsToCartForm


# Create your views here.
class AddTicketsToCartView(FormView):
	template_name = "carts/event_cart.html"
	form_class = TicketsToCartForm

	def get_success_url(self):
		view_name = "events:checkout"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_failure_url(self):
		view_name = "events:choose_tickets"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_event_landing(self):
		view_name = "events:landing"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_tickets(self, event):
		return Ticket.objects.filter(event=event, deleted=False)

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			raise Http404
		

	def post(self, request, *args, **kwargs):
		data = request.POST
		slug = kwargs['slug']
		event = self.get_event(slug)

		form = TicketsToCartForm(event=event, data=request.POST)
		if form.is_valid():
			return self.form_valid(form, request, event)
		else:
			return self.form_invalid(form)


	def get(self, request, *args, **kwargs):
		
		context = {}
		self.object = None
		slug = kwargs['slug']
		event = self.get_event(slug)
		tickets = self.get_tickets(event)

		# Check if the user should be here at all
		print(tickets.filter(sold_out=False).exists())
		if not tickets.filter(sold_out=False).exists():
			return HttpResponseRedirect(self.get_event_landing())

		form = TicketsToCartForm(event=event)

		cart_id = request.session.get('cart')
		if cart_id:
			cart = EventCart.objects.get(id=cart_id)
			cart_items = EventCartItem.objects.filter(event_cart=cart).delete()
		else:
			cart = EventCart.objects.create(event=event)
			request.session['cart'] = str(cart.id)
			request.session.modified = True


		context["form"] = form
		context["event"] = event
		context["tickets"] = tickets
		return render(request, self.template_name, context)


	def check_remaining_tickets(self, ticket, quantity):
		if quantity > (ticket.amount_available - ticket.amount_sold):
			return True
		else:
			return False

	def form_valid(self, form, request, event):
		cart_id = request.session.get('cart') 
		cart = EventCart.objects.get(id=cart_id)

		tickets = self.get_tickets(event)

		# Check if there are enough tickets to buy

		print(form.cleaned_data)

		for ticket in tickets:
			try:
				quantity = int(form.cleaned_data['%s' % (ticket.id)])
			except Exception as e:
				quantity = 0
			check = self.check_remaining_tickets(ticket, quantity)
			if check:
				tickets_left = ticket.amount_available - ticket.amount_sold
				messages.error(request, "%s tickets available for '%s'" % (tickets_left, ticket.title))
				return HttpResponseRedirect(self.get_failure_url())


		for ticket in tickets:
			
			donation_amount = None

			if ticket.donation:
				donation_amount = form.cleaned_data['%s_donation' % (ticket.id)]

			try:
				quantity = int(form.cleaned_data['%s' % (ticket.id)])
			except Exception as e:
				quantity = 0

			if quantity != 0:
				cart_item = EventCartItem.objects.create(event_cart=cart, ticket=ticket, quantity=quantity, donation_amount=donation_amount)


		valid_data = super(AddTicketsToCartView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))














