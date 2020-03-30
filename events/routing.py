# chat/routing.py
from django.urls import re_path
from django.urls import path

from events.consumers import ChatConsumer, LiveChatConsumer

websocket_urlpatterns = [

    path('ws/chat/<slug:slug>', LiveChatConsumer)
    # re_path(r'ws/chat/(?P<slug>\w+)/$', LiveChatConsumer),
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer),
    
]
