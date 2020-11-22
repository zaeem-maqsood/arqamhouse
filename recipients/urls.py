from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import AddRecipient, RecipientList, UpdateRecipient



app_name = "recipients"

urlpatterns = [
    path('', RecipientList.as_view(), name='list'),
    path('new', AddRecipient.as_view(), name='new_recipient'),
    path('<int:id>', UpdateRecipient.as_view(), name='update_recipient'),
]
