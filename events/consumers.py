from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from django.utils import timezone

from profiles.models import Profile
from events.models import EventLiveComment, EventLive, Event


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
        print(f"The user is {user}")

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
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user': user,
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
