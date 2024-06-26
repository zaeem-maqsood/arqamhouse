"""Arqam House houses 

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

from .views import (HouseHomePageView,
                    HouseContactPageView, AllArchivedListView, HouseEventsListView)

from donations.views import DonationView, DonationPublicListView, DonationPublicListLiveView, DonationGiftView, DonationGiftListView
from posts.views import EditPostView

from .urls import urlpatterns

urlpatterns += [

    path('', HouseHomePageView.as_view(), name='home_page'),
    path('donate', DonationView.as_view(), name='donate'),
    path('gift-donation', DonationGiftListView.as_view(), name='gift_donations'),
    path('gift-donation/<int:pk>', DonationGiftView.as_view(), name='gift_donate'),
    path('donations', DonationPublicListView.as_view(), name='public_donations'),
    path('donations/live', DonationPublicListLiveView.as_view(), name='public_donations_live'),
    path('recordings', AllArchivedListView.as_view(), name='house_recordings'),
    path('events', HouseEventsListView.as_view(), name='house_events'),
    path('contact', HouseContactPageView.as_view(), name='house_contact'),
    path('blog/<int:post_number>/edit', EditPostView.as_view(), name='edit_post'),

]
