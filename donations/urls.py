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
from django.urls import path, include

from donations.views import (DonationListView, DonationView, DonationTypeCreateView, DonationDashboardView, 
                             DonationTypeListView, DonationTypeUpdateView, DonationDetailView, update_payment_intent_amount)

app_name = "donations"

urlpatterns = [
    path('', DonationDashboardView.as_view(), name='dashboard'),
    path('all', DonationListView.as_view(), name='list'),
    path('types', DonationTypeListView.as_view(), name='types'),
    path('types/create', DonationTypeCreateView.as_view(), name='create_type'),
    path('types/<int:pk>', DonationTypeUpdateView.as_view(), name='update_type'),
    path('detail/<public_id>', DonationDetailView.as_view(), name='detail'),
    path('update_payment_intent_amount', update_payment_intent_amount, name='update_payment_intent_amount'),
]










