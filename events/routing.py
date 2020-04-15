# chat/routing.py
from django.urls import re_path
from django.urls import path

from events.consumers import LiveChatConsumer, LiveEventFeeConsumer

websocket_urlpatterns = [

    path('ws/chat/<slug:slug>', LiveChatConsumer),
    path('ws/live-event-fee/<slug:slug>', LiveEventFeeConsumer)
    
    
]
