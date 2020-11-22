"""Arqam House Events URL Configuration

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
from django.urls import path, include

from postcards.views import (
    PostCardListView, PostCardOrderView, PostCardManageOrdersView, PostCardBusinessListView, PostCardBusinessOrderViewStepOne, stripePayment, NonProfitPostCardListView,
    PostCardViewAllRecipients, PostcardSenderAddressList)

app_name = "postcards"

urlpatterns = [
    path('', PostCardListView.as_view(), name='list'),
    path('business', PostCardBusinessListView.as_view(), name='business_list'),
    path('manage', PostCardManageOrdersView.as_view(), name='manage'),
    path('non-profit/<slug:slug>', NonProfitPostCardListView.as_view(), name='non_profit_list'),
    path('<slug:slug>', PostCardOrderView.as_view(), name='detail'),
    path('<slug:slug>/sender-change', PostcardSenderAddressList.as_view(), name='order_view_senders'),
    path('<slug:slug>/recipients/', PostCardViewAllRecipients.as_view(), name='order_view_recipients'),
    path('ajax/stripe-payment', stripePayment, name='stripe_payment'),
    path('business/<slug:slug>/step-1', PostCardBusinessOrderViewStepOne.as_view(), name='business_step_1'),
]
