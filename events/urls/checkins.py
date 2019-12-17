from .base import *

from events.views import TestingQRCodeView

urlpatterns += [
    path('testing/qr-code', TestingQRCodeView.as_view(), name='qr_code'),
]
