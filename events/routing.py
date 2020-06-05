# chat/routing.py
from django.urls import re_path
from django.urls import path

from events.consumers import LiveChatConsumer, LiveEventFeeConsumer, LiveParticipantsView, LiveButtonCheckerConsumer

websocket_urlpatterns = [

    path('ws/chat/<slug:slug>', LiveChatConsumer),
    path('ws/live-event-fee/<slug:slug>', LiveEventFeeConsumer),
    path('ws/live-participants/<slug:slug>', LiveParticipantsView),
    path('ws/buttons/<slug:slug>', LiveButtonCheckerConsumer)
    
]
