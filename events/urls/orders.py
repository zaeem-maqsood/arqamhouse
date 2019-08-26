from .base import *
from events.views import OrderListView, OrderDetailView

urlpatterns += [

    path('<slug:slug>/orders/', OrderListView.as_view(), name='order_list'),
    path('<slug:slug>/orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),

]