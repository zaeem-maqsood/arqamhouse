from .base import *

from events.views import (LiveEventOptionsView, LiveEventHouseView, LiveEventViewerView, 
                          ArchivedListView, ArchivedDetailView, BroadcastCreateView, BroadcastUpdateView, LiveEventCommentsView)

urlpatterns += [

    path('<slug:slug>/live', LiveEventViewerView.as_view(), name='live_viewer'),
    path('<slug:slug>/archives', ArchivedListView.as_view(), name='archives'),
    path('<slug:slug>/archives/<int:pk>', ArchivedDetailView.as_view(), name='achrive_detail'),

    path('<slug:slug>/live/presenter', LiveEventHouseView.as_view(), name='live_presenter'),
    path('<slug:slug>/live/options', LiveEventOptionsView.as_view(), name='live_options'),
    path('<slug:slug>/live/comments', LiveEventCommentsView.as_view(), name='live_comments'),

    path('<slug:slug>/live/<int:pk>/create-facebook-broadcast', BroadcastCreateView.as_view(), name='broadcast_facebook', kwargs={"stream_type":"facebook"}),
    path('<slug:slug>/live/<int:pk>/create-youtube-broadcast', BroadcastCreateView.as_view(), name='broadcast_youtube', kwargs={"stream_type":"youtube"}),

    path('<slug:slug>/live/<int:pk>/broadcast-update/<int:broadcast_pk>', BroadcastUpdateView.as_view(), name='broadcast_update'),
]
