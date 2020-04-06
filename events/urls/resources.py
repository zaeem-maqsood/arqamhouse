from .base import *

from events.views import EventResourceListView, EventResourceCreateView, EventResourceUpdateView, EventResourceDetailView

urlpatterns += [

    path('<slug:slug>/resources', EventResourceListView.as_view(), name='resources'),

    path('<slug:slug>/resources/<int:pk>', EventResourceDetailView.as_view(),name='resource_detail'),

    path('<slug:slug>/resources/create/file', EventResourceCreateView.as_view(), name='create_resource_file', kwargs={"type":"file"}),
    path('<slug:slug>/resources/create/image', EventResourceCreateView.as_view(), name='create_resource_image', kwargs={"type":"image"}),
    path('<slug:slug>/resources/create/link', EventResourceCreateView.as_view(), name='create_resource_link', kwargs={"type":"link"}),
    path('<slug:slug>/resources/create/text', EventResourceCreateView.as_view(), name='create_resource_text', kwargs={"type":"text"}),

    path('<slug:slug>/resources/update/<int:pk>', EventResourceUpdateView.as_view(),name='update_resource'),
]
