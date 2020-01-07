from .base import *

from events.views import ListCheckInView, CheckinCreateView, CheckInView, CheckinUpdateView

urlpatterns += [
    path('<slug:slug>/checkins', ListCheckInView.as_view(), name='checkins'),
    path('<slug:slug>/checkins/create', CheckinCreateView.as_view(), name='create_checkin'),
    path('<slug:slug>/checkins/<int:pk>', CheckInView.as_view(), name='checkin'),
    path('<slug:slug>/checkins/update/<int:pk>', CheckinUpdateView.as_view(), name='checkin_update'),
]
