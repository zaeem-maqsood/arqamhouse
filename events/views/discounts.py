from .base import *

class DiscountUpdateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, CreateView):

    template_name = "events/discounts/discount_form.html"
    form_class = DiscountForm
    model = EventDiscount

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Exception as e:
            print(e)
            raise Http404
        return event

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        form = self.get_form()
        event = self.get_event(self.kwargs["slug"])
        tickets = Ticket.objects.filter(event=event, paid=True)
        context["update"] = True
        context["discount_code"] = self.object
        context["form"] = form
        context["tickets"] = tickets
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        context["house"] = self.get_house()
        return context

    def get_success_url(self):
        view_name = "events:list_discounts"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        self.object = EventDiscount.objects.get(id=pk)
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        self.object = EventDiscount.objects.get(id=pk)
        data = request.POST
        house = self.get_house()
        form = self.get_form()
        event = self.get_event(kwargs["slug"])

        if form.is_valid():
            return self.form_valid(form, request, event)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request, event):
        data = request.POST

        if "delete" in data:
            self.object.deleted = True
            self.object.save()
            messages.success(request, 'Code Deleted Successfully!')

        elif 'undo-delete' in data:
            self.object.deleted = False
            self.object.save()
            messages.success(request, 'Code Recovered Successfully!')

        else:
            house = self.get_house()
            self.object = form.save()
            self.object.event = event
            tickets = Ticket.objects.filter(event=event, paid=True)
            self.object.tickets.clear()
            for ticket in tickets:
                if str(ticket.id) in data:
                    self.object.tickets.add(ticket)
            messages.success(request, 'Discount Code Updated')
            
        valid_data = super(DiscountUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class DiscountCreateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, CreateView):

    template_name = "events/discounts/discount_form.html"
    form_class = DiscountForm
    model = EventDiscount

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Exception as e:
            print(e)
            raise Http404
        return event

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        form = self.get_form()
        event = self.get_event(self.kwargs["slug"])
        tickets = Ticket.objects.filter(event=event, paid=True)
        context["form"] = form
        context["tickets"] = tickets
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        context["house"] = self.get_house()
        return context

    def get_success_url(self):
        view_name = "events:list_discounts"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get(self, request, *args, **kwargs):
        self.object = None
        return render(request, self.template_name, self.get_context_data())

    
    def post(self, request, *args, **kwargs):
        self.object = None
        data = request.POST
        house = self.get_house()
        form = self.get_form()
        event = self.get_event(kwargs["slug"])

        if form.is_valid():
            return self.form_valid(form, request, event)
        else:
            return self.form_invalid(form)
    

    def form_valid(self, form, request, event):
        house = self.get_house()
        self.object = form.save()
        self.object.event = event
        tickets = Ticket.objects.filter(event=event, paid=True)

        data = request.POST

        for ticket in tickets:
            if str(ticket.id) in data:
                self.object.tickets.add(ticket)

        messages.success(request, 'Discount Code Created')
        valid_data = super(DiscountCreateView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



class DiscountsListView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):

    template_name = "events/discounts/list_discounts.html"

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Exception as e:
            print(e)
            raise Http404
        return event


    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *args, **kwargs):
        context = {}

        event = self.get_event(self.kwargs['slug'])
        context["event"] = event

        house = self.get_house()
        context["house"] = house
        
        discount_codes = EventDiscount.objects.filter(event=event)

        context["discount_codes"] = discount_codes
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context
