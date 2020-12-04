from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import OrderList, OrderDetail, OrderPublicDetail, LineOrderEdit


app_name = "orders"

urlpatterns = [
    path('', OrderList.as_view(), name='list'),
    path('<int:id>', OrderDetail.as_view(), name='detail'),
    path('<int:id>/<int:line_order_id>', LineOrderEdit.as_view(), name='edit'),
    path('<public_id>', OrderPublicDetail.as_view(), name='public_detail'),
]
