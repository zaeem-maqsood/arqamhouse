
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import (ProfileUpdateView, ProfileCreateView, LoginView, LogoutView,
                    load_cities, load_regions, UserDashboardView, activate_account, UserOrdersView, PasswordChangeView,
                    UserSubscribersView)


app_name="profiles"

urlpatterns = [

	path('dashboard', UserDashboardView.as_view(), name='dashboard'),
	path('login', LoginView.as_view(), name='login'),
	path('logout', LogoutView.as_view(), name='logout'),
	path('new', ProfileCreateView.as_view(), name='create'),

	path('orders', UserOrdersView.as_view(), name='orders'),
	path('subscribers', UserSubscribersView.as_view(), name='subscribers'),

	path('change-password/', PasswordChangeView.as_view(), name='change_password'),
	
	# Update Profile view
	path('update/', ProfileUpdateView.as_view(), name='update'),

	path('ajax/load-region/', load_regions, name='ajax_load_regions'),
	path('ajax/load-cities/', load_cities, name='ajax_load_cities'),  

	path('activate/<slug:uidb64>/<slug:token>/', activate_account, name='activate')

]
