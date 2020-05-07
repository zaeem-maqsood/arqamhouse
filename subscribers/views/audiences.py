from .base import *




class AudienceListView(HouseAccountMixin, ListView):
    model = Audience
    template_name = "subscribers/audiences/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        active_audiences = Audience.objects.filter(Q(house=house, event__active=True, donation_type__isnull=True) | Q(house=house, donation_type__deleted=False, event__isnull=True))
        past_audiences = Audience.objects.filter(Q(house=house, event__active=False, donation_type__isnull=True) | Q(house=house, donation_type__deleted=True, event__isnull=True))
        context["subscribers_tab"] = True
        context["dashboard_events"] = self.get_events()
        context["active_audiences"] = active_audiences
        context["past_audiences"] = past_audiences
        context["house"] = house
        return context


    def post(self, request, *args, **kwargs):
        data = request.POST
        print("It came to post")
        print(data)

        print(request.is_ajax())

        house = self.get_house()
        all_subscribers = Subscriber.objects.select_related('profile').filter(house=house, unsubscribed=False).order_by('-created_at')
        search_terms = data["search"].split()

        if data["search"] == '':
            subscribers = all_subscribers
        else:
            counter = 0
            for search_term in search_terms:
                if counter == 0:
                    subscribers = all_subscribers.filter(Q(profile__name__icontains=search_term) | Q(
                        profile__email__icontains=search_term))
                else:
                    subscribers = subscribers.filter(Q(profile__name__icontains=search_term) | Q(
                        profile__email__icontains=search_term))
                print(counter)
                counter += 1
        
        subscribers = subscribers[:100]
        print(subscribers)
        html = render_to_string('subscribers/subscribers-dynamic-table-body.html', {'subscribers': subscribers, 'request':request})
        return HttpResponse(html)




class AudienceView(HouseAccountMixin, View):
    template_name = "subscribers/audiences/detail.html"

    def get_audience(self, house):
        try:
            slug = self.kwargs["slug"]
            audience = Audience.objects.get(house=house, slug=slug)
            return audience
        except:
            raise Http404


    def get(self, request, *args, **kwargs):
        context = {}
        house = self.get_house()
        audience = self.get_audience(house)
        subscribers = audience.subscribers
        subscribers = subscribers.filter(unsubscribed=False)

        context["subscribers"] = subscribers
        context["audience"] = audience
        context["subscribers_tab"] = True
        context["house"] = house
        context["dashboard_events"] = self.get_events()

        return render(request, self.template_name, context)
