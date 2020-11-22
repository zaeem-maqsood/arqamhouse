
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import (ProfileUpdateView, ProfileCreateView, LoginView, LogoutView,
                    load_cities, load_regions, UserDashboardView, activate_account, UserOrdersView, PasswordChangeView,
                    UserSubscribersView, VerificationView, ChangePhoneNumberView, UserMenuPage, UserDonationsView, AddAddress,
                    AddressList, UpdateAddress)


app_name="profiles"

urlpatterns = [

	path('menu', UserMenuPage.as_view(), name='menu'),
	path('dashboard', UserDashboardView.as_view(), name='dashboard'),
	path('login', LoginView.as_view(), name='login'),
	path('verification/', VerificationView.as_view(), name='verification'),

	path('logout', LogoutView.as_view(), name='logout'),
	path('new', ProfileCreateView.as_view(), name='create'),

	path('recipients/', include('recipients.urls')),
	path('orders/', include('orders.urls')),

	path('addresses', AddressList.as_view(), name='address_list'),
	path('addresses/new', AddAddress.as_view(), name='add_address'),
	path('addresses/<int:id>', UpdateAddress.as_view(), name='update_address'),

	# path('donations', UserDonationsView.as_view(), name='donations'),
	# path('tickets', UserOrdersView.as_view(), name='tickets'),
	# path('subscribers', UserSubscribersView.as_view(), name='subscribers'),

	path('change-password/', PasswordChangeView.as_view(), name='change_password'),
	path('change-phone/', ChangePhoneNumberView.as_view(), name='change_phone'),
	
	# Update Profile view
	path('update/', ProfileUpdateView.as_view(), name='update'),

	path('ajax/load-region/', load_regions, name='ajax_load_regions'),
	path('ajax/load-cities/', load_cities, name='ajax_load_cities'),  

	path('activate/<slug:uidb64>/<slug:token>/', activate_account, name='activate')

]
