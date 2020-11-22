from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import OrderList, OrderDetail


app_name = "orders"

urlpatterns = [
    path('', OrderList.as_view(), name='list'),
    path('<int:id>', OrderDetail.as_view(), name='detail'),
]
