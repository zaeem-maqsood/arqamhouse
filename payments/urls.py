from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import PaymentListView, AddFundsView, PayoutView, PayoutSettingsListView, AddBankTransferView, UpdateBankTransferView

app_name="payments"

urlpatterns = [

    path('', PaymentListView.as_view(), name='list'),
    path('add-funds/', AddFundsView.as_view(), name='add_funds'),
    path('payout/', PayoutView.as_view(), name='payout'),
    path('payout-settings/', PayoutSettingsListView.as_view(), name='payout_settings_list'),
    path('add-bank/', AddBankTransferView.as_view(), name='add_bank'),
    path('bank/<int:bank_transfer_id>', UpdateBankTransferView.as_view(), name='update_bank'),
]
