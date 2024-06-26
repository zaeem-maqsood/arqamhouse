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

from .views import (HouseCreateView, HouseLandingView,
                    DashboardView, HouseUpdateView, AddUserToHouseView, HouseVerificationView, HouseSupportInfoView,
                    HouseHomePageView, HouseUserDetailView)

from donations.views import DonationListView


app_name="houses"

urlpatterns = [


	# Create House And User View
	path('new', HouseCreateView.as_view(), name='create'),

	# Langing Page For house
	path('dashboard', DashboardView.as_view(), name='dashboard'),

	# Update House
	path('update', HouseUpdateView.as_view(), name='update'),

    # Verifiy House
	path('support-info', HouseSupportInfoView.as_view(), name='support_info'),

	# Manage Users
	path('manage', AddUserToHouseView.as_view(), name='manage'),

    # Manage Individual Users
	path('manage/<int:pk>', HouseUserDetailView.as_view(), name='manage_house_user'),

    # Verifiy House
	path('verify', HouseVerificationView.as_view(), name='verify'),

    # # Donations
	# path('manage-donations', DonationListView.as_view(), name='donations'),

]
