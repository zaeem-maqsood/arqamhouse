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

from .views import TicketCreateView, TicketListView, TicketUpdateView 
from carts.views import AddTicketsToCartView

app_name="tickets"

urlpatterns = [

    path('', AddTicketsToCartView.as_view(), name='choose_tickets'),
    path('list', TicketListView.as_view(), name='list_tickets'),
    path('create/free', TicketCreateView.as_view(), name='create_free_ticket', kwargs={"type":"free"}),
    path('create/paid', TicketCreateView.as_view(), name='create_paid_ticket', kwargs={"type":"paid"}),
    path('create/donation', TicketCreateView.as_view(), name='create_donation_ticket', kwargs={"type":"donation"}),
    path('update/<slug:ticket_slug>', TicketUpdateView.as_view(), name='update_ticket'),
]