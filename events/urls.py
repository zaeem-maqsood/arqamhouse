"""Arqam House Events URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import (EventLandingView, EventCreateView, EventUpdateView, PastEventsView, EventCheckoutView,
                    EventCheckinCreateView, EventDashboardView)

from carts.views import AddTicketsToCartView

app_name="events"

urlpatterns = [

    path('create', EventCreateView.as_view(), name='create'),
    path('past', PastEventsView.as_view(), name='past'),
    path('<slug:slug>/', EventLandingView.as_view(), name='landing'),
    path('<slug:slug>/dashboard', EventDashboardView.as_view(), name='dashboard'),
    path('<slug:slug>/update', EventUpdateView.as_view(), name='update'),
    path('<slug:slug>/checkout', EventCheckoutView.as_view(), name='checkout'),
    path('<slug:slug>/create-checkin/', EventCheckinCreateView.as_view(), name='create_checkin'),
    path('<slug:slug>/tickets/', include('tickets.urls')),
    path('<slug:slug>/questions/', include('questions.urls')),
    path('<slug:slug>/orders/', include('orders.urls')),
    path('<slug:slug>/attendees/', include('attendees.urls')),
    path('<slug:slug>/payout/', include('payouts.urls')),
]