from .base import *

from events.views import (EventLandingView, EventCreateView, EventUpdateView, PastEventsView, EventCheckoutView, EventDashboardView,
                          AddTicketsToCartView)


urlpatterns += [

    path('create', EventCreateView.as_view(), name='create'),
    path('past', PastEventsView.as_view(), name='past'),
    path('<slug:slug>/', AddTicketsToCartView.as_view(), name='landing'),
    path('<slug:slug>/dashboard', EventDashboardView.as_view(), name='dashboard'),
    path('<slug:slug>/update', EventUpdateView.as_view(), name='update'),
    path('<slug:slug>/checkout', EventCheckoutView.as_view(), name='checkout'),
    path('<slug:slug>/questions/', include('questions.urls')),
]
