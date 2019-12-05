from .base import *
from events.views import OrderListView, OrderDetailView

urlpatterns += [

    path('<slug:slug>/orders/', OrderListView.as_view(), name='order_list'),
    path('<slug:slug>/orders/<public_id>/', OrderDetailView.as_view(), name='order_detail'),
    
]