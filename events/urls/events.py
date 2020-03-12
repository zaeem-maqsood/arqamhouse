from .base import *

from events.views import (EventCreateView, EventUpdateView, PastEventsView, EventCheckoutView, EventDashboardView,
                          AddTicketsToCartView, ChannelsView, ChannelsRoomView, EventSendToSubscribersView, EventTrafficView,
                          EventVenueView, EventImageView, EventDescriptionView, EventURLView)


urlpatterns += [


    path('create', EventCreateView.as_view(), name='create'),
    path('past', PastEventsView.as_view(), name='past'),
    path('<slug:slug>/', AddTicketsToCartView.as_view(), name='landing'),
    path('<slug:slug>/dashboard', EventDashboardView.as_view(), name='dashboard'),
    path('<slug:slug>/send-to-subscribers', EventSendToSubscribersView.as_view(), name='send_to_subscribers'),
    path('<slug:slug>/update', EventUpdateView.as_view(), name='update'),
    path('<slug:slug>/update/url', EventURLView.as_view(), name='update_url'),
    path('<slug:slug>/update/venue', EventVenueView.as_view(), name='update_venue'),
    path('<slug:slug>/update/image', EventImageView.as_view(), name='update_image'),
    path('<slug:slug>/update/description', EventDescriptionView.as_view(), name='update_description'),
    path('<slug:slug>/checkout', EventCheckoutView.as_view(), name='checkout'),
    path('<slug:slug>/traffic', EventTrafficView.as_view(), name='traffic'),
    path('<slug:slug>/questions/', include('questions.urls')),

    path('testing/chat', ChannelsView.as_view(), name='channels_test'),
    path('testing/chat/<str:room_name>/', ChannelsRoomView.as_view(), name='channels_test_room'),
]
