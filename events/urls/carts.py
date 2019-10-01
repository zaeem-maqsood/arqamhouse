from .base import *

from events.views import AddTicketsToCartView

urlpatterns += [
    # path('<slug:slug>/tickets', AddTicketsToCartView.as_view(), name='choose_tickets'),
]
