
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import ProfileUpdateView, ProfileCreateView, ProfileDetailView, LoginView, LogoutView


app_name="profiles"

urlpatterns = [

	path('login', LoginView.as_view(), name='login'),
	path('logout', LogoutView.as_view(), name='logout'),
	path('new', ProfileCreateView.as_view(), name='create'),
	path('<slug:slug>', ProfileDetailView.as_view(), name='detail'),
	# Update Profile view
	path('update/<slug:slug>', ProfileUpdateView.as_view(), name='update'),


]