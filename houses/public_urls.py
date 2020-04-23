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

from .views import (HouseHomePageView, HouseContactPageView)

from donations.views import DonationView, DonationPublicListView

from .urls import urlpatterns

urlpatterns += [

    path('', HouseHomePageView.as_view(), name='home_page'),
    path('donate', DonationView.as_view(), name='donate'),
    path('donations', DonationPublicListView.as_view(), name='public_donations'),
    path('contact', HouseContactPageView.as_view(), name='house_contact'),

]
