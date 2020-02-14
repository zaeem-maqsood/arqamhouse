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
from django.contrib.auth import views as auth_views

from houses.views import DashboardView, ConnectVerificationView, ChangeEntityTypeView
from .views import HomePageView, ReportErrorView, ApplePayVerificationView
from events.views import OrderPublicDetailView

urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
    path('report', ReportErrorView.as_view(), name='report'),
    path('change-entity', ChangeEntityTypeView.as_view(), name='change_entity'),
    path('verification', ConnectVerificationView.as_view(), name='verification'),
    path('house/', include('houses.urls')),
    path('profile/', include('profiles.urls')),
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
    path('questions/', include('questions.urls')),
    path('payments/', include('payments.urls')),
    path('subscribers/', include('subscribers.urls')),
    path('orders/<public_id>/', OrderPublicDetailView.as_view(), name='order_detail_public'),
    path('.well-known/apple-developer-merchantid-domain-association', ApplePayVerificationView.as_view(), name='apple_verification'),


    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/', auth_views.PasswordResetView.as_view(html_email_template_name='registration/password_reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),  name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# if settings.DEBUG:
# 	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
# 	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
