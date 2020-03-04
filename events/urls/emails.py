from .base import *

from events.views import EventConfirmationEmailView, EventEmailView

urlpatterns += [

    path('<slug:slug>/emails', EventEmailView.as_view(), name='emails'),
    path('<slug:slug>/emails/email-confirmation', EventConfirmationEmailView.as_view(), name='email_confirmation'),
]
