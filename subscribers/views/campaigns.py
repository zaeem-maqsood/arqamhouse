from .base import *
from subscribers.forms import GenericCampaignForm
from subscribers.tasks import send_campaign_emails


class UnsubscribeFromEmailView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        
        try:
            subscriber_id = data["subscriber_id"]
            subscriber = Subscriber.objects.get(id=int(subscriber_id))
            subscriber.unsubscribed = True
            subscriber.save()
            view_name = "houses:home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": subscriber.house.slug}))
        except:
            view_name = "home"
            return HttpResponseRedirect(reverse(view_name))
        


class CampaignTrackerView(View):


    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
    
        try:
            campaign_id = data["campaign_id"]
            subscriber_id = data["subscriber_id"]
            campaign = Campaign.objects.get(id=int(campaign_id))
            try:
                subscriber = Subscriber.objects.get(id=int(subscriber_id))
                campaign.subscribers_seen.add(subscriber)
                campaign.save()
            except:
                pass
        except:
            pass
        return HttpResponse("")


class CampaignContentView(HouseAccountMixin, View):
    template_name = "emails/test_campaign_email.html"

    def get(self, request, *args, **kwargs):
        context = {}
        slug = kwargs["slug"]
        house = self.get_house()
        try:
            campaign = Campaign.objects.get(slug=slug)
        except:
            raise Http404

        context["campaign"] = campaign
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        context["campaigns_tab"] = True
        return render(request, self.template_name, context)


class CampaignDetailView(HouseAccountMixin, View):
    template_name = "subscribers/campaigns/detail.html"

    def get(self, request, *args, **kwargs):
        context = {}
        slug = kwargs["slug"]
        house = self.get_house()
        try:
            campaign = Campaign.objects.get(slug=slug)
        except:
            raise Http404

        if campaign.deleted:
            return redirect('subscribers:campaign_list')

        context["campaign"] = campaign
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        context["campaigns_tab"] = True
        return render(request, self.template_name, context)



class CampaignUpdateView(HouseAccountMixin, UpdateView):
    model = Campaign
    form_class = GenericCampaignForm
    template_name = "subscribers/campaigns/update.html"

    def get_success_url(self):
        view_name = "subscribers:campaign_list"
        return reverse(view_name)

    def get_campaign(self):
        slug = self.kwargs['slug']
        campaign = Campaign.objects.get(slug=slug)
        return campaign

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()

        subscribers = Subscriber.objects.filter(house=house, unsubscribed=False)
        form = self.get_form()

        if self.object.audience:
            audience = self.object.audience
            subscribers = self.object.audience.subscribers.all()
            context["audience"] = audience

        context["dashboard_events"] = self.get_events()
        context["campaigns_tab"] = True
        context["subscribers"] = subscribers
        context["form"] = form
        context["campaign"] = self.object
        context["house"] = house
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_campaign()

        if not self.object.draft:
            return redirect('subscribers:campaign_list')

        if self.object.deleted:
            return redirect('subscribers:campaign_list')

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

        if 'delete' in data:
            self.object.deleted = True
            self.object.save()
            messages.info(request, f'Campaign {self.object.name} Deleted')
            view_name = "subscribers:campaign_list"
            return HttpResponseRedirect(reverse(view_name))


        if 'test' in data:
            print(form.cleaned_data)
            if form.cleaned_data.get('test_email') != '':
                test_email = form.cleaned_data.get('test_email')
                self.send_test_email(test_email)
                messages.success(request, f'Test Email Sent to {test_email}!')
                view_name = "subscribers:campaign_update"
                return HttpResponseRedirect(reverse(view_name, kwargs={"slug": self.object.slug}))
            else:
                self.send_test_email(house.email)
                messages.success(request, f'Test Email Sent to {house.email}!')
                view_name = "subscribers:campaign_update"
                return HttpResponseRedirect(reverse(view_name, kwargs={"slug": self.object.slug}))
            

        elif "nuke" in data:

            if self.object.event:
                subscribers = Subscriber.objects.filter(house=house, unsubscribed=False, events=self.object.event)
            else:
                subscribers = Subscriber.objects.filter(house=house, unsubscribed=False)

            for subscriber in subscribers:
                subscriber.campaigns_total += 1
                subscriber.save()

            subscribers = list(subscribers)
            self.object.subscribers_sent_to.add(*subscribers)
            self.object.draft = False
            self.object.save()
            task = send_campaign_emails.delay(self.object.id)
            messages.success(request, 'Campaign sent!')

        else:
            messages.success(request, 'Campaign Updated Successfully!')
            view_name = "subscribers:campaign_update"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": self.object.slug}))

        valid_data = super(CampaignUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



    def send_test_email(self, to_email):

        campaign = self.get_campaign()

        # Compose Email
        subject = f"[Test] {campaign.subject}"
        context = {}
        context["campaign"] = campaign
        context["house"] = campaign.house
        html_content = render_to_string('emails/test_campaign_email.html', context)
        text_content = strip_tags(html_content)

        from_email = f"{campaign.house.name} <info@arqamhouse.com>"
        to = [to_email]
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

    def get_audience(self, house):
        audience_slug = self.kwargs['slug']
        try:
            audience = Audience.objects.get(slug=audience_slug, house=house)
            return audience
        except Exception as e:
            print(e)
            raise Http404

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        subscribers = Subscriber.objects.filter(house=house)

        form = self.get_form()

        if 'slug' in self.kwargs:
            audience = self.get_audience(house)
            subscribers = audience.subscribers.all()
            context["audience"] = audience

        context["subscribers"] = subscribers
        context["dashboard_events"] = self.get_events()
        context["campaigns_tab"] = True
        context["form"] = form
        context["house"] = house
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        house = self.get_house()

        if not Subscriber.objects.filter(house=house).exists():
            return redirect('subscribers:campaign_list')

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

        if 'slug' in self.kwargs:
            audience = self.get_audience(house)
            self.object.audience = audience

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
        campaigns = Campaign.objects.filter(house=house, deleted=False).order_by("-created_at")

        context["dashboard_events"] = self.get_events()
        context["campaigns_tab"] = True
        context["campaigns"] = campaigns
        context["house"] = house
        return context
