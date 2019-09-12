from .base import *

from events.models import EventEmailConfirmation
from django.core.mail import send_mail
from events.forms import EventEmailConfirmationForm



class EventConfirmationEmailView(HouseAccountMixin, UserPassesTestMixin, UpdateView):
    model = EventEmailConfirmation
    form_class = EventEmailConfirmationForm
    template_name = "events/emails/confirmation_email.html"

    def get_success_url(self):
        view_name = "events:update"
        return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get_context_data(self, *args, **kwargs):
        context = {}
        slug = self.kwargs['slug']
        event = self.get_event(slug)
        house = self.get_house()
        # self.object = event.eventemailconfirmation


        context["form"] = EventEmailConfirmationForm()
        context["house"] = house
        context["event"] = event

        context["update_event"] = True
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.POST

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        self.object = form.save()

        messages.success(request, 'Event Updated')
        valid_data = super(EventConfirmationEmailView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))