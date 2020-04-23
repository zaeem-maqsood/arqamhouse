from .base import *
from events.models import EventResource
from events.forms import ResourceFileForm, ResourceImageForm, ResourceLinkForm, ResourceTextForm


class EventResourceUpdateView(HouseAccountMixin, UpdateView):
    model = EventResource
    template_name = "events/resources/form.html"

    def get_success_url(self):
        view_name = "events:resource_detail"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"], "pk": self.kwargs["pk"]})

    def get_context_data(self, *args, **kwargs):
        context = {}
        event = self.get_event()
        house = self.get_house()

        if self.object.file:
            form = ResourceFileForm(instance=self.object)
            resource_type = 'file'
        elif self.object.image:
            form = ResourceImageForm(instance=self.object)
            resource_type = 'image'
        elif self.object.text:
            form = ResourceTextForm(instance=self.object)
            resource_type = 'text'
        else:
            form = ResourceLinkForm(instance=self.object)
            resource_type = 'link'

        context["resource_type"] = resource_type
        context["form"] = form
        context["event"] = event
        context["house"] = house
        return context

    def get_event(self):
        event_slug = self.kwargs['slug']
        try:
            event = Event.objects.get(slug=event_slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get_event_resource(self):
        event_resource_id = self.kwargs["pk"]
        try:
            event_resource = EventResource.objects.get(id=event_resource_id)
            return event_resource
        except Exception as e:
            print(e)
            raise Http404


    def get(self, request, *args, **kwargs):
        self.object = self.get_event_resource()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_event_resource()
        data = request.POST
        house = self.get_house()

        if self.object.file:
            form = ResourceFileForm(data, request.FILES, instance=self.object)
        elif self.object.image:
            form = ResourceImageForm(data, request.FILES, instance=self.object)
        elif self.object.text:
            form = ResourceTextForm(data, request.FILES, instance=self.object)
        else:
            form = ResourceLinkForm(data, request.FILES, instance=self.object)


        event = self.get_event()

        if form.is_valid():
            return self.form_valid(form, request, event)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request, event):
        house = self.get_house()
        form.instance.event = event
        self.object = form.save()

        print(form.cleaned_data)

        messages.success(request, 'Resource Added!')
        valid_data = super(EventResourceUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))





class EventResourceCreateView(HouseAccountMixin, CreateView):
    model = EventResource
    template_name = "events/resources/form.html"

    def get_success_url(self):
        view_name = "events:resources"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get_context_data(self, *args, **kwargs):
        context = {}
        event = self.get_event()
        house = self.get_house()
        resource_type = self.kwargs['type']

        if resource_type == 'file':
            form = ResourceFileForm()
        elif resource_type == 'image':
            form = ResourceImageForm()
        elif resource_type == 'text':
            form = ResourceTextForm()
        else:
            form = ResourceLinkForm()
        
        context["resource_type"] = resource_type
        context["form"] = form
        context["event"] = event
        context["house"] = house
        return context

    def get_event(self):
        event_slug = self.kwargs['slug']
        try:
            event = Event.objects.get(slug=event_slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        self.object = None
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = None
        data = request.POST
        house = self.get_house()
        
        resource_type = self.kwargs['type']

        if resource_type == 'file':
            form = ResourceFileForm(data, request.FILES)
        elif resource_type == 'image':
            form = ResourceImageForm(data, request.FILES)
        elif resource_type == 'text':
            form = ResourceTextForm(data, request.FILES)
        else:
            form = ResourceLinkForm(data, request.FILES)

        event = self.get_event()

        if form.is_valid():
            return self.form_valid(form, request, event)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request, event):
        house = self.get_house()
        form.instance.event = event
        self.object = form.save()

        print(form.cleaned_data)

        messages.success(request, 'Resource Added!')
        valid_data = super(EventResourceCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class EventResourceDetailView(View):
    model = EventResource
    template_name = "events/resources/detail.html"

    def get_event_resource(self):
        event_resource_id = self.kwargs["pk"]
        try:
            event_resource = EventResource.objects.get(id=event_resource_id)
            return event_resource
        except Exception as e:
            print(e)
            raise Http404

    def get_event(self):
        event_slug = self.kwargs['slug']
        try:
            event = Event.objects.get(slug=event_slug)
            return event
        except Exception as e:
            print(e)
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

    def get_context_data(self, *args, **kwargs):
        context = {}
        event = self.get_event()
        house = event.house
        resource = self.get_event_resource()

        context["is_owner"] = self.check_if_user_is_owner(event)
        context["resource"] = resource
        context["event"] = event
        context["house"] = house
        return context

    def get(self, request, *args, **kwargs):
        event = self.get_event()
        return render(request, self.template_name, self.get_context_data())






class EventResourceListView(View):
    model = EventResource
    template_name = "events/resources/list.html"

    def get_success_url(self):
        view_name = "subscribers:campaign_list"
        return reverse(view_name)

    def get_event(self):
        event_slug = self.kwargs['slug']
        try:
            event = Event.objects.get(slug=event_slug)
            return event
        except Exception as e:
            print(e)
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

    def get_context_data(self, *args, **kwargs):
        context = {}
        event = self.get_event()
        house = event.house
        resources = EventResource.objects.filter(event=event)

        context["is_owner"] = self.check_if_user_is_owner(event)
        context["resources"] = resources
        context["event"] = event
        context["house"] = house
        return context


    def get(self, request, *args, **kwargs):
        event = self.get_event()
        return render(request, self.template_name, self.get_context_data())

