from .base import *

from events.views import LiveEventCreateView, LiveEventHouseView, LiveEventViewerView

urlpatterns += [

    path('<slug:slug>/live', LiveEventViewerView.as_view(), name='live_viewer'),

    path('<slug:slug>/live/presenter', LiveEventHouseView.as_view(), name='live_presenter'),

]
