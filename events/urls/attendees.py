from .base import *
from events.views import AttendeeListView, AttendeeDetailView


urlpatterns += [

    path('<slug:slug>/attendees/', AttendeeListView.as_view(), name='attendee_list'),
    path('<slug:slug>/attendees/<slug:attendee_id>/', AttendeeDetailView.as_view(), name='attendee_detail'),

    
]