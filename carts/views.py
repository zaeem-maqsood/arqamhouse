
from django.conf import settings
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse


from events.models import Event
from tickets.models import Ticket
from .models import EventCart, EventCartItem
from .forms import TicketsToCartForm


# Create your views here.
class AddTicketsToCartView(FormView):
	template_name = "carts/event_cart.html"
	form_class = TicketsToCartForm

	def get_success_url(self):
		view_name = "events:checkout"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_tickets(self, event):
		return Ticket.objects.filter(event=event)

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


	def form_valid(self, form, request, event):
		cart_id = request.session.get('cart') 
		cart = EventCart.objects.get(id=cart_id)

		tickets = self.get_tickets(event)
		for ticket in tickets:
			
			donation_amount = None

			if ticket.donation:
				donation_amount = form.cleaned_data['%s_donation' % (ticket.id)]

			quantity = int(form.cleaned_data['%s' % (ticket.id)])
			if quantity != 0:
				cart_item = EventCartItem.objects.create(event_cart=cart, ticket=ticket, quantity=quantity, donation_amount=donation_amount)


		valid_data = super(AddTicketsToCartView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))














