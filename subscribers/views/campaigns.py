from .base import *
from subscribers.forms import GenericCampaignForm
from subscribers.tasks import send_campaign_emails


class UnsubscribeFromEmailView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        print("OMG IT CAME HERE")
        print(data)
        subscriber_id = data["subscriber_id"]
        try:
            subscriber = Subscriber.objects.get(id=int(subscriber_id))
            subscriber.unsubscribed = True
            subscriber.save()
            print("We got unsubscriber")
            print(subscriber)
            view_name = "houses:home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": subscriber.house.slug}))
        except:
            view_name = "home"
            return HttpResponseRedirect(reverse(view_name))
        


class CampaignTrackerView(View):


    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        print("OMG IT CAME HERE")
        print(data)
        campaign_id = data["campaign_id"]
        subscriber_id = data["subscriber_id"]
        try:
            campaign = Campaign.objects.get(id=int(campaign_id))
            try:
                subscriber = Subscriber.objects.get(id=int(subscriber_id))
                campaign.subscribers_seen.add(subscriber)
                campaign.save()
            except:
                pass
        except:
            pass
        print("We got campaign")
        print(campaign)
        return HttpResponse("")


class CampaignContentView(HouseAccountMixin, View):
    template_name = "emails/test_campaign_email.html"

    def get(self, request, *args, **kwargs):
        context = {}
        pk = kwargs["pk"]
        house = self.get_house()
        try:
            campaign = Campaign.objects.get(id=pk)
        except:
            raise Http404
        context["campaign"] = campaign
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        return render(request, self.template_name, context)


class CampaignDetailView(HouseAccountMixin, View):
    template_name = "subscribers/campaigns/detail.html"

    def get(self, request, *args, **kwargs):
        context = {}
        pk = kwargs["pk"]
        house = self.get_house()
        try:
            campaign = Campaign.objects.get(id=pk)
        except:
            raise Http404
        context["campaign"] = campaign
        context["house"] = house
        context["dashboard_events"] = self.get_events()

        return render(request, self.template_name, context)



class CampaignUpdateView(HouseAccountMixin, UpdateView):
    model = Campaign
    form_class = GenericCampaignForm
    template_name = "subscribers/campaigns/update.html"

    def get_success_url(self):
        view_name = "subscribers:campaign_list"
        return reverse(view_name)

    def get_campaign(self):
        pk = self.kwargs['pk']
        campaign = Campaign.objects.get(id=pk)
        return campaign

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()

        subscribers = Subscriber.objects.filter(house=house)
        form = self.get_form()

        context["dashboard_events"] = self.get_events()
        context["subscribers"] = subscribers
        context["form"] = form
        context["campaign"] = self.object
        context["house"] = house
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_campaign()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = request.POST

        self.object = self.get_campaign()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        print(data)
        self.object = form.save()
        house = self.get_house()

        if 'test' in data:
            self.send_test_email()
            messages.success(request, f'Test Email Sent to {house.email}!')

        elif "nuke" in data:
            subscribers = Subscriber.objects.filter(house=house)
            subscribers = list(subscribers)
            self.object.subscribers_sent_to.add(*subscribers)
            self.object.draft = False
            self.object.save()
            task = send_campaign_emails.delay(self.object.id)
            messages.success(request, 'Campaign sent!')

        else:
            messages.success(request, 'Campaign Updated Successfully!')

        valid_data = super(CampaignUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



    def send_test_email(self):

        campaign = self.get_campaign()

        # Compose Email
        subject = f"[Test] {campaign.subject}"
        context = {}
        context["campaign"] = campaign
        context["house"] = campaign.house
        html_content = render_to_string('emails/test_campaign_email.html', context)
        text_content = strip_tags(html_content)

        from_email = f"{campaign.house.name} <info@arqamhouse.com>"
        to = [campaign.house.email]
        email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return "Done"




class CampaignCreateView(HouseAccountMixin, CreateView):
    model = Campaign
    form_class = GenericCampaignForm
    template_name = "subscribers/campaigns/create.html"

    def get_success_url(self):
        view_name = "subscribers:campaign_list"
        return reverse(view_name)

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()

        subscribers = Subscriber.objects.filter(house=house)
        form = self.get_form()
        context["dashboard_events"] = self.get_events()
        context["form"] = form
        context["house"] = house
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = request.POST

        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        house = self.get_house()
        self.object = form.save(commit=False)
        self.object.house = house
        self.object.total = 0
        self.object.score = 0
        self.object.seen = 0
        self.object.save()
        messages.success(request, 'Campaign Created Successfully!')
        valid_data = super(CampaignCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



class CampaignListView(HouseAccountMixin, ListView):
    model = Campaign
    template_name = "subscribers/campaigns/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        campaigns = Campaign.objects.filter(house=house).order_by("-created_at")

        context["dashboard_events"] = self.get_events()
        context["campaigns"] = campaigns
        context["house"] = house
        return context
