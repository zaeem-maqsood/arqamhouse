"""arqamhouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from organizations.views import DashboardView, ConnectVerificationView, ChangeEntityTypeView
from .views import HomePageView

urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
    path('change-entity', ChangeEntityTypeView.as_view(), name='change_entity'),
    path('verification', ConnectVerificationView.as_view(), name='verification'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('o/', include('organizations.urls')),
    path('profile/', include('profiles.urls')),
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
    path('payouts/', include('payouts.urls')),
    path('descriptions/', include('descriptions.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 