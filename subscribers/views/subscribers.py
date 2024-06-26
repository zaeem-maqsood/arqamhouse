from .base import *

# Create your views here.


class SubscriberCreateView(HouseAccountMixin, FormView):
    model = Subscriber
    template_name = "subscribers/add_subscriber.html"

    def get_success_url(self):
        view_name = "subscribers:list"
        return reverse(view_name)

    def get(self, request, *args, **kwargs):
        self.object = None
        form = AddSubscriberForm()
        return self.render_to_response(self.get_context_data(form=form, request=request, subscribers_tab=True))


    def post(self, request, *args, **kwargs):
        data = request.POST
        form = AddSubscriberForm(data=data)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)


    def form_valid(self, form, request):

        house = self.get_house()
        # Get email and password from the form
        email = form.cleaned_data.get("email")
        name = form .cleaned_data.get("name")

        passed_events = Event.objects.filter(house=house, active=False, deleted=False).count()

        email = email.lower()
        
        # First see if a profile exists with that email
        try:
            profile = Profile.objects.get(email=email)
        except:
            
            profile = Profile.objects.create_user(name=name, email=email, password=get_random_string(length=10))


        # Check if they are already subscribed
        try:
            subscriber = Subscriber.objects.get(profile=profile, house=house)
            form.add_error("email", "This Subscriber has previously unsubscribed. They must manually subscribe themselves.")
            return self.render_to_response(self.get_context_data(form=form, request=request))
        except:
            subscriber = Subscriber.objects.create(profile=profile, house=house, events_total=1, attendance_total=1)

        messages.success(request, 'Subscriber added!')

        valid_data = super(SubscriberCreateView, self).form_valid(form)
        return valid_data

    
    def form_invalid(self, form, request):
        print(form.errors)
        print(form.non_field_errors)
        return self.render_to_response(self.get_context_data(form=form, request=request, subscribers_tab=True))

        


class SubscriberDetailView(HouseAccountMixin, View):
    template_name = "subscribers/detail.html"

    def get(self, request, *args, **kwargs):
        context = {}
        slug = kwargs["slug"]
        house = self.get_house()
        subscriber = Subscriber.objects.get(profile__slug=slug, house=house)
        seen_campaigns = Campaign.objects.filter(subscribers_seen=subscriber).order_by("created_at")
        donations = Donation.objects.filter(donation_type__house=house, email=subscriber.profile.email)
        orders = EventOrder.objects.filter(email=subscriber.profile.email, event__house=house).order_by("created_at")
        attendees = Attendee.objects.filter(order__in=orders).count()

        result_list = sorted(chain(seen_campaigns, orders, donations), key=attrgetter('created_at'))
        result_list.reverse()

        context["subscribers_tab"] = True
        context["result_list"] = result_list
        context["seen_campaigns"] = seen_campaigns
        context["subscriber"] = subscriber
        context["attendees"] = attendees
        context["orders"] = orders
        context["house"] = house
        context["dashboard_events"] = self.get_events()

        return render(request, self.template_name, context)


class SubscriberListView(HouseAccountMixin, ListView):
    model = Subscriber
    template_name = "subscribers/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        subscribers = Subscriber.objects.filter(house=house, unsubscribed=False)
        context["subscribers_tab"] = True
        context["dashboard_events"] = self.get_events()
        context["subscribers"] = subscribers
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
