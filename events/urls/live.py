from .base import *

from events.views import LiveEventCreateView, LiveEventHouseView, LiveEventViewerView

urlpatterns += [

    path('<slug:slug>/live', LiveEventViewerView.as_view(), name='live_viewer'),

    path('<slug:slug>/live/presenter', LiveEventHouseView.as_view(), name='live_presenter'),
    path('<slug:slug>/live/presenter/<mode>', LiveEventHouseView.as_view(), name='live_presenter'),

    path('<slug:slug>/live/create/<mode>', LiveEventCreateView.as_view(), name='live_create'),
]
