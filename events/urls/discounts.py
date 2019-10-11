from .base import *

from events.views import DiscountsListView, DiscountCreateView, DiscountUpdateView

urlpatterns += [
    path('<slug:slug>/discounts', DiscountsListView.as_view(), name='list_discounts'),
    path('<slug:slug>/discounts/create', DiscountCreateView.as_view(), name='create_discount'),
    path('<slug:slug>/discounts/<int:pk>', DiscountUpdateView.as_view(), name='update_discount'),
]
