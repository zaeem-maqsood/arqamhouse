from .base import *

from events.forms import CheckinForm
from events.models import Checkin, Ticket, Event, Attendee, EventOrder

# Create your views here.
class CheckInView(HouseAccountMixin, View):
    template_name = "events/checkins/checkin.html"

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except:
            raise Http404
        return event

    def get_checkin(self, pk):
        try:
            checkin = Checkin.objects.get(id=pk)
        except:
            raise Http404
        return checkin

    def get(self, request, *args, **kwargs):
        context = {}
        event = self.get_event(kwargs['slug'])
        checkin = self.get_checkin(kwargs['pk'])
        amount = checkin.attendee_set.all().count()
        if checkin.exclusive:
            tickets = checkin.tickets.all()
            attendees = Attendee.objects.filter(order__event=event, ticket__in=tickets).order_by('order__created_at')
        else:
            attendees = Attendee.objects.filter(order__event=event).order_by('order__created_at')

        context["amount"] = amount
        context["attendees"] = attendees
        context["checkin"] = checkin
        context["event"] = event
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        print("It came to post")
        print(data)

        event = self.get_event(kwargs['slug'])
        checkin = self.get_checkin(kwargs['pk'])
        if checkin.exclusive:
            tickets = checkin.tickets.all()
            all_attendees = Attendee.objects.filter(order__event=event, ticket__in=tickets).order_by('order__created_at')
        else:
            all_attendees = Attendee.objects.filter(order__event=event).order_by('order__created_at')

        # If the user is searching for an attendee
        if 'search' in data:
            search_terms = data["search"].split()

            if data["search"] == '':
                attendees = all_attendees
            else:
                counter = 0
                for search_term in search_terms:
                    print(search_term)
                    if counter == 0:
                        attendees = all_attendees.filter(Q(name__icontains=search_term) | Q(ticket__title__icontains=search_term) | Q(
                            order__name__icontains=search_term) | Q(order__public_id=search_term))
                    else:
                        attendees = attendees.filter(Q(name__icontains=search_term) | Q(ticket__title__icontains=search_term) | Q(
                            order__name__icontains=search_term) | Q(order__public_id=search_term))
                    counter += 1

            attendees = attendees[:100]
            print(attendees)
            html = render_to_string('events/checkins/attendees-dynamic-table-body.html', {'attendees': attendees, 'request': request, 'checkin': checkin})
            return HttpResponse(html)

        else:
            attendee_id = data["attendee_id"]

            try:
                attendee = Attendee.objects.get(unique_id=attendee_id)
                if checkin in attendee.checkins.all():
                    attendee.checkins.remove(checkin)
                    message = "%s checked out of %s" % (attendee.name, checkin.name)
                    color = "#bb0a0a"
                else:
                    attendee.checkins.add(checkin)
                    message = "%s checked in to %s" % (attendee.name, checkin.name)
                    color = "#0abb87"
                amount = checkin.attendee_set.all().count()
                html = render_to_string('events/checkins/attendees-dynamic-table-body.html', {'attendees': all_attendees, 'request': request, 'checkin': checkin})
                data = {"html": html, "message": message, "color": color, "amount": amount}
                return JsonResponse(data)

            except Exception as e:
                print(e)
                return HttpResponse("error")
            



class ListCheckInView(HouseAccountMixin, View):
    template_name = "events/checkins/list_checkin.html"

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except:
            raise Http404
        return event

    def get(self, request, *args, **kwargs):
        context = {}
        event = self.get_event(self.kwargs['slug'])

        checkins = Checkin.objects.filter(event=event, deleted=False)
        if checkins.count() > 1:
            context["checkins"] = checkins
        elif checkins.count() == 1:
            checkin = checkins.first()
            return HttpResponseRedirect(checkin.get_checkin_view())
        else:
            return HttpResponseRedirect(event.create_checkin_view())
        
        context["event"] = event
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        data = request.POST
        print("It came to post")
        print(data)
        
        return HttpResponse("Checked IN!")



class CheckinUpdateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, CreateView):

    template_name = "events/checkins/checkin_form.html"
    form_class = CheckinForm
    model = Checkin

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Exception as e:
            print(e)
            raise Http404
        return event

    def get_checkin(self, pk):
        try:
            checkin = Checkin.objects.get(id=pk)
        except:
            raise Http404
        return checkin

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        form = self.get_form()
        event = self.get_event(self.kwargs["slug"])

        context["update"] = True
        context["checkin"] = self.object
        context["event"] = event
        context["form"] = form
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        context["house"] = self.get_house()
        return context

    def get_success_url(self):
        view_name = "events:checkins"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get(self, request, *args, **kwargs):
        self.object = self.get_checkin(kwargs["pk"])
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_checkin(kwargs["pk"])
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

        house = self.get_house()
        self.object = form.save()
        self.object.event = event
        messages.success(request, 'Checkin Updated')
        valid_data = super(CheckinUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



class CheckinCreateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, CreateView):

    template_name = "events/checkins/checkin_form.html"
    form_class = CheckinForm
    model = Checkin

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
        context["event"] = event
        context["form"] = form
        context["tickets"] = tickets
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        context["house"] = self.get_house()
        return context

    def get_success_url(self):
        view_name = "events:checkins"
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

        exclusiive = form.cleaned_data.get("exclusive")
        if exclusiive:
            for ticket in tickets:
                if str(ticket.id) in data:
                    self.object.tickets.add(ticket)

        messages.success(request, 'Checkin Created')
        valid_data = super(CheckinCreateView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
