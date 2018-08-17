
from .models import Event

class EventMixin(object):

	active_events = []
	inactive_events = []

	def get_active_events(self, organization):
		events = Event.objects.active_events().filter(organization=organization).order_by('start')
		return events
