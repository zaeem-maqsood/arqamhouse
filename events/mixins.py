
from .models import Event

class EventMixin(object):

	active_events = []
	inactive_events = []

	def get_inactive_events(self, organization):
		events = Event.objects.inactive_events().filter(organization=organization).order_by('start')
		return events

	def get_deleted_events(self, organization):
		events = Event.objects.deleted_events().filter(organization=organization).order_by('start')
		return events
