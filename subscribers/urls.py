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

from subscribers.views import (SubscriberListView, SubscriberDetailView, SubscriberCreateView,
                               CampaignListView, CampaignUpdateView, CampaignTrackerView, UnsubscribeFromEmailView,
                               CampaignCreateView, CampaignDetailView, CampaignContentView, AudienceView, AudienceListView)

app_name = "subscribers"

urlpatterns = [

    path('', SubscriberListView.as_view(), name='list'),
    path('campaigns', CampaignListView.as_view(), name='campaign_list'),
    path('audiences', AudienceListView.as_view(), name='audience_list'),


    path('create', SubscriberCreateView.as_view(), name='create'),
    path('<slug:slug>', SubscriberDetailView.as_view(), name='detail'),

    path('audience/<slug:slug>', AudienceView.as_view(), name='audience_detail'),

    path('campaigns/create', CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/create/audience/<slug:slug>', CampaignCreateView.as_view(), name='campaign_create_audience'),
    path('campaigns/update/<slug:slug>', CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/details/<slug:slug>', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/detail/<slug:slug>/content', CampaignContentView.as_view(), name='campaign_detail_content'),
    path('campaigns/tracker', CampaignTrackerView.as_view(), name='campaign_tracker'),
    path('campaigns/unsubscribe-from-email', UnsubscribeFromEmailView.as_view(), name='campaign_unsubscribe_from_email'),
]










