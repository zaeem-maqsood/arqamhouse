from .base import *
from events.models import EventLive, EventLiveComment, EventLiveArchive, EventLiveBroadcast, EventLiveFee
from profiles.mixins import ProfileMixin
from django.utils.crypto import get_random_string

from events.forms import BroadcastFacebookForm, BroadcastYoutubeForm

from opentok import MediaModes

import boto3
from botocore.client import Config


def get_event_live(event_live_pk):
    try:
        event_live = EventLive.objects.get(id=event_live_pk)
        return event_live
    except Exception as e:
        print(e)
        raise Http404


class BroadcastUpdateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):
    model = EventLiveBroadcast
    template_name = "events/live/broadcast.html"

    def get_success_url(self):
        view_name = "events:live_options"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get_context_data(self, *args, **kwargs):
        context = {}
        event = get_event(self.kwargs['slug'])
        house = self.get_house()

        if self.object.facebook_url:
            stream_type = 'facebook'
            form = BroadcastFacebookForm(instance=self.object)
        else:
            stream_type = 'youtube'
            form = BroadcastYoutubeForm(instance=self.object)            

        context["update"] = True
        context["stream_type"] = stream_type
        context["form"] = form
        context["event"] = event
        context["house"] = house
        return context

    def get_event_live_broadcast(self):
        event_live_broadcast_pk = self.kwargs['broadcast_pk']
        try:
            event_live_broadcast = EventLiveBroadcast.objects.get(id=event_live_broadcast_pk)
            return event_live_broadcast
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        self.object = self.get_event_live_broadcast()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_event_live_broadcast()
        data = request.POST
        house = self.get_house()

        if self.object.facebook_url:
            stream_type = 'facebook'
            form = BroadcastFacebookForm(data, request.FILES, instance=self.object)
        else:
            stream_type = 'youtube'
            form = BroadcastYoutubeForm(data, request.FILES, instance=self.object)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        self.object = form.save()

        if 'delete' in request.POST:
            self.object.delete()
            messages.info(request, 'Broadcast Stream Deleted!')
            view_name = "events:live_options"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": self.kwargs['slug']}))


        messages.success(request, 'Broadcast Stream Updated!')
        valid_data = super(BroadcastUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))







class BroadcastCreateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, CreateView):
    model = EventLiveBroadcast
    template_name = "events/live/broadcast.html"

    def get_success_url(self):
        view_name = "events:live_options"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get_context_data(self, *args, **kwargs):
        context = {}
        event = get_event(self.kwargs['slug'])
        house = self.get_house()

        stream_type = self.kwargs['stream_type']

        if stream_type == 'facebook':
            form = BroadcastFacebookForm()
        else:
            form = BroadcastYoutubeForm()
        
        context["stream_type"] = stream_type
        context["form"] = form
        context["event"] = event
        context["house"] = house
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = None
        data = request.POST
        house = self.get_house()
        
        stream_type = self.kwargs['stream_type']

        if stream_type == 'facebook':
            form = BroadcastFacebookForm(data, request.FILES)
        else:
            form = BroadcastYoutubeForm(data, request.FILES)

        event_live = get_event_live(self.kwargs['pk'])

        if form.is_valid():
            return self.form_valid(form, request, event_live)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request, event_live):
        form.instance.event_live = event_live
        self.object = form.save()

        print(form.cleaned_data)

        messages.success(request, 'Broadcast Added!')
        valid_data = super(BroadcastCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))









class ArchivedDetailView(View):
    template_name = "events/live/archive_detail.html"

    def allow_entry(self, event):
        
        # First check for profile
        profile = get_profile(self.request.user)
        if profile:

            # Second Check if house user
            try:
                house_user = HouseUser.objects.get(house=event.house, profile=profile)
                return True
            except:
                return False
        else:
            return False


    def check_if_user_is_owner(self, event):
        profile = get_profile(self.request.user)

        try:
            if event.house == profile.house:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def get_archive(self):
        archive_pk = self.kwargs['pk']
        try:
            event_live_archive = EventLiveArchive.objects.get(id=archive_pk)
            return event_live_archive
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        event = get_event(self.kwargs['slug'])
        house = event.house

        is_owner = self.check_if_user_is_owner(event)

        from urllib.parse import unquote
        event_live_archive = self.get_archive()
        event_live_archive.views += 1
        event_live_archive.save()

        s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        response = s3_client.generate_presigned_url('get_object', Params={
                                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': event_live_archive.archive_location}, ExpiresIn=3600)
        # print(unquote(response))
        context["event_live_archive_url"] = response
        context["is_owner"] = is_owner
        context["event_live_archive"] = event_live_archive
        context["profile"] = get_profile(self.request.user)
        context["event"] = event
        context["house"] = house
        return render(request, self.template_name, context)



    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        event = get_event(self.kwargs['slug'])
        event_live = EventLive.objects.get(event=event)
        event_live_archive = self.get_archive()

       

        if 'delete' in data:

            s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            response = s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=event_live_archive.archive_location,
            )
            print(response)
            event_live_archive.delete()

        if 'update' in data:

            try:
                archive_title = data["archive_title"]
                archive_description = data["archive_description"]
                event_live_archive.name = archive_title
                event_live_archive.description = archive_description
                event_live_archive.save()
                view_name = "events:achrive_detail"
                return HttpResponseRedirect(reverse(view_name, kwargs={"slug": event.slug, "pk": event_live_archive.id}))
            except Exception as e:
                print(e)
        
        view_name = "events:archives"
        return HttpResponseRedirect(reverse(view_name, kwargs={"slug": event.slug}))











class ArchivedListView(View):
    template_name = "events/live/archives.html"


    def allow_entry(self, event):
        
        # First check for profile
        profile = get_profile(self.request.user)
        if profile:

            # Second Check if house user
            try:
                house_user = HouseUser.objects.get(house=event.house, profile=profile)
                return True
            except:
                return False
        else:
            return False

    def check_if_user_is_owner(self, event):
        profile = get_profile(self.request.user)

        try:
            if event.house == profile.house:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def get(self, request, *args, **kwargs):
        context = {}
        event = get_event(self.kwargs['slug'])
        house = event.house

        event_live = EventLive.objects.get(event=event)
        event_live_archives = EventLiveArchive.objects.filter(event_live=event_live).order_by("created_at")

        is_owner = self.check_if_user_is_owner(event)

        context["is_owner"] = is_owner
        context["event_live_archives"] = event_live_archives
        context["profile"] = get_profile(self.request.user)
        context["event"] = event
        context["house"] = house
        return render(request, self.template_name, context)













class LiveEventViewerView(View):
    template_name = "events/live/viewer.html"


    def allow_entry(self, event):
        
        # First check for profile
        profile = get_profile(self.request.user)
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


    def get(self, request, *args, **kwargs):
        context = {}
        event = get_event(self.kwargs['slug'])
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
        context["profile"] = get_profile(self.request.user)
        context["slug_json"] = mark_safe(json.dumps(slug))
        context["event_live"] = event_live
        context["facing_mode"] = event_live.facing_mode
        context["api_key"] = api_key
        context["session_id"] = session_id
        context["token"] = token

        context["event"] = event
        context["house"] = house
        return render(request, self.template_name, context)






def load_audience(request):
    json_data = json.loads(request.body)
    if json_data:
        print(json_data)
        slug = json_data['slug']
        event = get_event(slug)
        event_live = EventLive.objects.get(event=event)
        print(event_live)
        people = event_live.live_audience.all()
        html = render_to_string('events/live/audience.html', {'people': people})
        return JsonResponse({'html': html})



class LiveEventHouseView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):
    template_name = "events/live/presenter.html"


    def get(self, request, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = get_event(self.kwargs['slug'])

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
            session = opentok.create_session(media_mode=MediaModes.routed)
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

        
        event_live_broadcasts = EventLiveBroadcast.objects.filter(event_live=event_live)
        print(event_live_broadcasts)
        context["event_live_broadcasts"] = event_live_broadcasts

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



    def post(self, request, *args, **kwargs):
        import json

        data = request.POST
        print(data)

        json_data = json.loads(request.body)

        event = get_event(self.kwargs['slug'])
        event_name = event.slug
        event_live = EventLive.objects.get(event=event)
        session_id = event_live.session_id
        api_key = settings.OPEN_TOK_API_KEY
        api_secret = settings.OPEN_TOK_SECRECT_KEY
        opentok = OpenTok(api_key, api_secret)

        all_archives =  EventLiveArchive.objects.filter(event_live=event_live).order_by("-created_at")
        total_archives = all_archives.count()
        last_archive = total_archives.first()
        
        if json_data:

            try:
                value = json_data['record']
                print(value)

                if value:
                    print("value")
                    archive = opentok.start_archive(session_id, name=event_name, resolution="1280x720")
                    print("Did it come here")
                    print("the archive is")
                    print(archive)
                    print("the archive is")
                    archive_location = f"{api_key}/{archive.id}/archive.mp4"
                    event_live_archive = EventLiveArchive.objects.create(name=f"{event.title} - {total_archives}", description=f"Virtual Event recording #{total_archives} for {event.title}", event_live=event_live, archive_id=archive.id, archive_location=archive_location)
                else:
                    print("No value")
                    opentok.stop_archive(last_archive.archive_id)

            except Exception as e:
                print(e)
                print("The exception happend")



            try:
                event_live_broadcasts = EventLiveBroadcast.objects.filter(event_live=event_live)
                rtmp = []
                for event_live_broadcast in event_live_broadcasts:
                    rtmp_dict = {}
                    print(event_live_broadcast.name)
                    rtmp_dict["id"] = event_live_broadcast.name
                    if event_live_broadcast.facebook_url:
                        rtmp_dict["serverUrl"] = event_live_broadcast.facebook_url
                    else:
                        rtmp_dict["serverUrl"] = event_live_broadcast.youtube_url
                    rtmp_dict["streamName"] = event_live_broadcast.stream_key
                    rtmp.append(rtmp_dict)


                print(rtmp)
                value = json_data['broadcast']
                print(value)

                if value:
                    session_id = session_id
                    options = {
                        'layout': {
                            'type': 'bestFit',
                        },
                        'maxDuration': 7200,
                        'outputs': {
                        'hls': {},
                        'rtmp': rtmp
                        },
                        'resolution': '1280x720'
                    }

                    broadcast = opentok.start_broadcast(session_id, options)
                    broadcast_id = broadcast.id
                    event_live.broadcast_id = broadcast_id
                    event_live.save()
                    
                else:
                    broadcast = opentok.stop_broadcast(event_live.broadcast_id)

            except Exception as e:
                print(e)

        return HttpResponse("Done")












class LiveEventOptionsView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):
    model = EventLive
    template_name = "events/live/options.html"

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = get_event(self.kwargs['slug'])

        event_live = EventLive.objects.get(event=event)
        event_live_broadcasts = EventLiveBroadcast.objects.filter(event_live=event_live)

        context["event_live"] = event_live
        context["event_live_broadcasts"] = event_live_broadcasts
        context["event"] = event
        context["dashboard_events"] = self.get_events()
        context["event_tab"] = True
        context["house"] = house
        return context


    def get(self, request, *args, **kwargs):
        event = get_event(self.kwargs['slug'])

        try:
            event_live = EventLive.objects.get(event=event)
        except Exception as e:
            print(e)
            api_key = settings.OPEN_TOK_API_KEY
            api_secret = settings.OPEN_TOK_SECRECT_KEY
            opentok = OpenTok(api_key, api_secret)
            session = opentok.create_session(media_mode=MediaModes.routed)
            session_id = session.session_id
            event_live = EventLive.objects.create(event=event, session_id=session_id)


        if not event.secret_live_id:
            secret_live_id = get_random_string(length=32)
            event.secret_live_id = secret_live_id
            event.save()

        if not event.secret_archive_id:
            secret_archive_id = get_random_string(length=32)
            event.secret_archive_id = secret_archive_id
            event.save()

        
        return render(request, self.template_name, self.get_context_data())


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        event = get_event(self.kwargs['slug'])

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

        if 'archive' in data:
            archive = data['archive']
            if archive == "true":
                archive = True
            else:
                archive = False

            event.allow_non_ticket_archive_viewers = archive
            event.save()

        if 'refresh_archive' in data:
            secret_archive_id = get_random_string(length=32)
            event.secret_archive_id = secret_archive_id
            event.save()

        return HttpResponse("Done")


        
    







class LiveEventCommentsView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):
    template_name = "events/live/comments.html"

    def get_success_url(self):
        view_name = "subscribers:campaign_list"
        return reverse(view_name)


    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = get_event(self.kwargs['slug'])
        event_live = EventLive.objects.get(event=event)
        event_live_comments = EventLiveComment.objects.filter(event_live=event_live).order_by("created_at")

        context["event_live"] = event_live
        context["event_live_comments"] = event_live_comments
        context["event"] = event
        context["dashboard_events"] = self.get_events()
        context["event_tab"] = True
        context["house"] = house
        return context


    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        if 'comment_id' in data:
            comment_id = data['comment_id']
            event_live_comment = EventLiveComment.objects.get(id=comment_id).delete()

        event = get_event(self.kwargs['slug'])
        event_live = EventLive.objects.get(event=event)

        if 'delete_all' in data:
            event_live_comments = EventLiveComment.objects.filter(event_live=event_live).delete()

        event_live_comments = EventLiveComment.objects.filter(event_live=event_live).order_by("created_at")
        html = render_to_string('events/live/dynamic-comments-section.html', {'event_live_comments': event_live_comments})
        return HttpResponse(html)
