"""Arqam House Organizations 

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

from .views import OrganizationAndUserCreateView, OrganizationLandingView


app_name="organizations"

urlpatterns = [


	# Create Organization And User View
	path('new', OrganizationAndUserCreateView.as_view(), name='create'),

	# Langing Page For Organization
	path('<slug:slug>/', OrganizationLandingView.as_view(), name='detail'),

	# Update Organization
	# path('<slug:slug>/update', EventDetailView.as_view(), name='update'),


	# Deactivate Organization
	# path('<slug:slug>/deactivate', EventDetailView.as_view(), name='deactivate'),

]