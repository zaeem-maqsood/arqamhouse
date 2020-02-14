from .base import *


# Create your views here.
class AddTicketsToCartView(FormView):
	template_name = "carts/event_cart.html"
	form_class = TicketsToCartForm

	def get_success_url(self):
		view_name = "events:checkout"
		return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

	def get_failure_url(self):
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

	def check_if_user_is_owner(self, event):
		profile = self.request.user

		try:
			if event.house == profile.house:
				return True
			else:
				return False
		except Exception as e:
			print(e)
			return False


	def post(self, request, *args, **kwargs):
		data = request.POST
		
		slug = kwargs['slug']
		event = self.get_event(slug)
		form = TicketsToCartForm(event=event, data=request.POST)
		
		owner = self.check_if_user_is_owner(event)
		if owner:
			house_created = True
		else:
			house_created = False

		if 'checkout-no-pay' in data:
			pay = False
		else:
			pay = True
			
		if form.is_valid():
			return self.form_valid(form, request, event, pay, house_created)
		else:
			return self.form_invalid(form)



	def get(self, request, *args, **kwargs):
		
		context = {}
		self.object = None
		slug = kwargs['slug']
		event = self.get_event(slug)

		# Check if event should be archived or not
		archive_past_events(event)

		tickets = self.get_tickets(event)

		# if not tickets.filter(sold_out=False).exists():
		# 	return HttpResponseRedirect(self.get_event_landing())

		# Check if event is deleted or archived.
		# if event.deleted or not event.active:
		# 	return HttpResponseRedirect(self.get_event_landing())


		form = TicketsToCartForm(event=event)

		cart_id = request.session.get('cart')
		if cart_id:
			cart = EventCart.objects.get(id=cart_id)
			cart_items = EventCartItem.objects.filter(event_cart=cart).delete()
		else:
			cart = EventCart.objects.create(event=event)
			request.session['cart'] = str(cart.id)
			request.session.modified = True

		owner = self.check_if_user_is_owner(event)

		discount_code = EventDiscount.objects.filter(event=event).exists()
		context["discount_code"] = discount_code

		house_users = HouseUser.objects.filter(house=event.house, profile__is_superuser=False)

		context["house_users"] = house_users
		context["owner"] = owner
		context["form"] = form
		context["event"] = event
		context["tickets"] = tickets
		context["time"] = timezone.now()
		return render(request, self.template_name, context)


	def check_remaining_tickets(self, ticket, quantity):
		if quantity > (ticket.amount_available - ticket.amount_sold):
			return True
		else:
			return False

	def form_valid(self, form, request, event, pay, house_created):
		cart_id = request.session.get('cart') 
		cart = EventCart.objects.get(id=cart_id)

		if EventDiscount.objects.filter(event=event).exists():
			cart.discount_code = None
			discount_code = form.cleaned_data["discount_code"]
			try:
				event_discount = EventDiscount.objects.get(event=event, code=discount_code, deleted=False, finished=False)
				cart.discount_code = event_discount
				cart.invalid_discount_code = False
			except Exception as e:
				print(e)
				print(discount_code)
				if discount_code == "":
					cart.invalid_discount_code = False
				else:
					cart.invalid_discount_code = True
			cart.save()

		# Delete all cart items before proceeding
		cart_items = EventCartItem.objects.filter(event_cart=cart).delete()

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
				if tickets_left == 1:
					messages.error(request, "Sorry, there is only %s '%s' ticket left." % (tickets_left, ticket.title))
				else:
					messages.error(request, "Sorry, there are only %s '%s' tickets left." % (tickets_left, ticket.title))
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

		if cart.total == 0.00:
			pay = False
		cart.house_created = house_created
		cart.pay = pay
		cart.save()
		valid_data = super(AddTicketsToCartView, self).form_valid(form)
		return valid_data


	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))














