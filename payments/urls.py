from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import PaymentListView, AddFundsView, PayoutView, PayoutSettingsListView, AddETransferView, UpdateETransferView

app_name="payments"

urlpatterns = [

    path('', PaymentListView.as_view(), name='list'),
    path('add-funds/', AddFundsView.as_view(), name='add_funds'),
    path('payout/', PayoutView.as_view(), name='payout'),
    path('payout-settings/', PayoutSettingsListView.as_view(), name='payout_settings_list'),
    path('add-etransfer/', AddETransferView.as_view(), name='add_e_transfer'),
    path('etransfer/<int:etransfer_id>', UpdateETransferView.as_view(), name='update_e_transfer'),
]