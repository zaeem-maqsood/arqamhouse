from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import PayoutHistoryView, PayoutDetailView

app_name="payments"

urlpatterns = [

    path('', PayoutHistoryView.as_view(), name='all_payouts'),
    path('<int:pk>', PayoutDetailView.as_view(), name='detail'),
]