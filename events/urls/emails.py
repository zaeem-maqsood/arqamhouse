from .base import *

from events.views import EventConfirmationEmailView

urlpatterns += [
    path('<slug:slug>/email-confirmation', EventConfirmationEmailView.as_view(), name='email_confirmation'),
]