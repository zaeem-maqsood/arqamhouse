from .base import *
from subscribers.forms import GenericCampaignForm


class CampaignTrackerView(HouseAccountMixin, View):


    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        print("OMG IT CAME HERE")
        print(data)
        campaign = Campaign.objects.get(id=1)
        campaign.draft = True
        campaign.save()
        return HttpResponse("")


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

        if 'test' in data:
            self.send_test_email()
            messages.success(request, 'Test Email Sent!')


        elif "Remove" in data:
            self.object.image = None
            self.object.save()
            messages.warning(request, 'Event image successfully removed')
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




class CampaignListView(HouseAccountMixin, ListView):
    model = Campaign
    template_name = "subscribers/campaigns/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        campaigns = Campaign.objects.filter(house=house).order_by("-updated_at")

        context["dashboard_events"] = self.get_events()
        context["campaigns"] = campaigns
        context["house"] = house
        return context
