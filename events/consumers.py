from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
import decimal
from django.utils import timezone

from profiles.models import Profile
from events.models import EventLiveComment, EventLive, Event, EventLiveFee
from payments.models import ArqamHouseServiceFee


class LiveEventFeeConsumer(WebsocketConsumer):

    def connect(self):
        print("did it come here live event fee")
        print(self.scope['url_route']['kwargs']['slug'])
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = 'live_event_fee_%s' % self.slug

        event_slug = self.scope['url_route']['kwargs']['slug']
        event = Event.objects.get(slug=event_slug)
        event_live = EventLive.objects.get(event=event)

        try:
            event_live_fee = EventLiveFee.objects.get(event_live=event_live, processed=False)
            event_live_fee.presenters = event_live_fee.presenters + 1
            event_live_fee.save()
        except Exception as e:
            print(e)
            event_live_fee = EventLiveFee.objects.create(event_live=event_live, presenters=1)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        print("We have disconnected from the fee calculation")

        event_slug = self.scope['url_route']['kwargs']['slug']
        event = Event.objects.get(slug=event_slug)
        event_live = EventLive.objects.get(event=event)

        try:
            event_live_fee = EventLiveFee.objects.get(event_live=event_live, processed=False)
            event_live_fee.presenters = event_live_fee.presenters - 1
            event_live_fee.save()
        except Exception as e:
            print(e)


        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        stream_amount = text_data_json['stream_amount']
        recording = text_data_json['recording']
        broadcasting = text_data_json['broadcasting']
        participants = text_data_json['participants']

        event_slug = self.scope['url_route']['kwargs']['slug']
        event = Event.objects.get(slug=event_slug)
        event_live = EventLive.objects.get(event=event)

        subscribed_mins = participants * 2
        if recording:
            archived_mins = 2
        else:
            archived_mins = 0

        try:
            event_live_fee = EventLiveFee.objects.get(event_live=event_live, processed=False)
            
            if event_live_fee.presenters > 1:
                subscribed_mins = subscribed_mins / event_live_fee.presenters
                archived_mins = archived_mins / event_live_fee.presenters

            event_live_fee.subscribed_mins = event_live_fee.subscribed_mins + subscribed_mins
            event_live_fee.archived_mins = event_live_fee.archived_mins + archived_mins
            event_live_fee.save()
        except Exception as e:
            print(e)
            print("The event live fee is not")

        print(f"The stream amount is {stream_amount}")
        print(f"The recording is {recording}")
        print(f"The broadcasting is {broadcasting}")
        print(f"The participants is {participants}")

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'live_event_fee_method',
                'stream_amount': stream_amount,
                'recording': recording,
                'broadcasting': broadcasting,
                'participants': participants
            }
        )

    # Receive message from room group
    def live_event_fee_method(self, event):
        stream_amount = event['stream_amount']
        recording = event['recording']
        broadcasting = event['broadcasting']
        participants = event['participants']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'stream_amount': stream_amount,
            'recording': recording,
            'broadcasting': broadcasting,
            'participants': participants,
        }))



class LiveChatConsumer(WebsocketConsumer):

    def connect(self):
        print("did it come here")
        print(self.scope['url_route']['kwargs']['slug'])
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = 'chat_%s' % self.slug

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = text_data_json['user']
        name = text_data_json['name']
        print(f"The user is {user}")
        print(f"The user is {name}")

        event_slug = self.scope['url_route']['kwargs']['slug']

        try:
            profile = Profile.objects.get(email=user)
            print(profile)
            event = Event.objects.get(slug=event_slug)
            event_live = EventLive.objects.get(event=event)
            event_live_comment = EventLiveComment.objects.create(
                event_live=event_live, profile=profile, comment=message)
        except:
            pass

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': profile.email,
                'name': profile.name
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        user = event['user']
        name = event['name']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'name': name
        }))



class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = text_data_json['user']
        print(f"The user is {user}")

        profile = Profile.objects.get(email=user)
        print(profile)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': profile.name,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))
