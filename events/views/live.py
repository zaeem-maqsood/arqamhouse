from .base import *
from events.models import EventLive, EventLiveComment
from profiles.mixins import ProfileMixin
from django.utils.crypto import get_random_string


# Add ProfileMixin after to make it so users have to login
class LiveEventViewerView(View):
    template_name = "events/live/viewer.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def allow_entry(self, event):
        
        # First check for profile
        profile = self.get_profile()
        if profile:

            # Second Check if house user
            try:
                house_user = HouseUser.objects.get(house=event.house, profile=profile)
                return True
            except:
                pass

            # Third Check if event order exists for the user
            event_order = EventOrder.objects.filter(email=profile.email).exists()
            if event_order:
                return True
            else:
                return False
        else:
            return False


    def get_event(self):
        event_slug = self.kwargs['slug']
        try:
            event = Event.objects.get(slug=event_slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        event = self.get_event()
        house = event.house

        if not event.allow_non_ticket_live_viewers:
            allow_entry = self.allow_entry(event)
        else:
            allow_entry = True

        data = request.GET
        if 'secret' in data:
            if data['secret'] == event.secret_live_id:
                allow_entry = True
            else: 
                allow_entry = False

        if not allow_entry:
            context["allow_entry"] = False

        else:
            context["allow_entry"] = True

        try:
            event_live = EventLive.objects.get(event=event)
            event_live_comments = EventLiveComment.objects.filter(event_live=event_live).order_by("created_at")
            context["event_live_comments"] = event_live_comments
        except Exception as e:
            view_name = "events:landing"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": event.slug}))


        if settings.DEBUG:
            context["local"] = True
        else:
            context["local"] = False

        session_id = event_live.session_id
        api_key = settings.OPEN_TOK_API_KEY
        api_secret = settings.OPEN_TOK_SECRECT_KEY
        opentok = OpenTok(api_key, api_secret)
        token = opentok.generate_token(session_id)

        slug = self.kwargs["slug"]
        context["profile"] = self.get_profile()
        context["slug_json"] = mark_safe(json.dumps(slug))
        context["event_live"] = event_live
        context["facing_mode"] = event_live.facing_mode
        context["api_key"] = api_key
        context["session_id"] = session_id
        context["token"] = token

        context["event"] = event
        context["house"] = house
        return render(request, self.template_name, context)





class LiveEventHouseView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):
    template_name = "events/live/presenter.html"

    def get_event(self):
        event_slug = self.kwargs['slug']
        try:
            event = Event.objects.get(slug=event_slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = self.get_event()

        try:
            event_live = EventLive.objects.get(event=event)
            session_id = event_live.session_id
            api_key = settings.OPEN_TOK_API_KEY
            api_secret = settings.OPEN_TOK_SECRECT_KEY
            opentok = OpenTok(api_key, api_secret)
            token = opentok.generate_token(session_id)

        except Exception as e:
            print(e)
            
            api_key = settings.OPEN_TOK_API_KEY
            api_secret = settings.OPEN_TOK_SECRECT_KEY
            opentok = OpenTok(api_key, api_secret)
            session = opentok.create_session()
            session_id = session.session_id
            token = session.generate_token()
            event_live = EventLive.objects.create(event=event, session_id=session_id)

        try:
            profile = Profile.objects.get(email=str(request.user))
        except:
            view_name = "events:dashboard"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": event.slug}))

        if settings.DEBUG:
            context["local"] = True
        else:
            context["local"] = False

        slug = self.kwargs["slug"]
        context["slug_json"] = mark_safe(json.dumps(slug))
        context["event_live"] = event_live

        event_live_comments = EventLiveComment.objects.filter(event_live=event_live).order_by("created_at")
        context["event_live_comments"] = event_live_comments
        context["profile"] = profile
            
        context["api_key"] = api_key
        context["session_id"] = session_id
        context["token"] = token

        context["event"] = event
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        context["event_tab"] = True
        return render(request, self.template_name, context)



class LiveEventOptionsView(HouseAccountMixin, View):
    model = EventLive
    template_name = "events/live/options.html"

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

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = self.get_event()

        context["event"] = event
        context["dashboard_events"] = self.get_events()
        context["event_tab"] = True
        context["house"] = house
        return context


    def get(self, request, *args, **kwargs):
        event = self.get_event()
        if not event.secret_live_id:
            secret_live_id = get_random_string(length=32)
            event.secret_live_id = secret_live_id
            event.save()
        return render(request, self.template_name, self.get_context_data())


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        event = self.get_event()

        if 'value' in data:
            value = data['value']

            if value == "true":
                value = True
            else:
                value = False

            event.allow_non_ticket_live_viewers = value
            event.save()

        if 'refresh' in data:
            secret_live_id = get_random_string(length=32)
            event.secret_live_id = secret_live_id
            event.save()

        return HttpResponse("Done")


        
    
