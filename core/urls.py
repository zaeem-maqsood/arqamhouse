from django.conf.urls import url
from .views import image_upload, file_upload
from django.urls import path, include

urlpatterns = [
    path('image_upload/<slug:house_slug>', image_upload, name='froala_editor_image_upload'),
    path('file_upload', file_upload, name='froala_editor_file_upload'),
]
