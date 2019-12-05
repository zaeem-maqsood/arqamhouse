from .base import *
from events.models import Attendee, EventOrderRefund, EventRefundRequest

admin.site.register(Attendee)
admin.site.register(EventOrderRefund)
admin.site.register(EventRefundRequest)
