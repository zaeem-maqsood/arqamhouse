
from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from houses.models import House, HouseUser
from profiles.models import Profile
from events.models import Event


class EventSecurityMixin(object):

	def test_func(self):
		house_users = HouseUser.objects.filter(profile=self.request.user)
		event = Event.objects.get(slug=self.kwargs['slug'])
		print(event)
		for house_user in house_users:
			if event.house == house_user.house:
				return True
		return False


class EventMixin(object):

	active_events = []
	inactive_events = []

	def get_inactive_events(self, house):
		events = Event.objects.inactive_events().filter(house=house).order_by('start')
		return events

	def get_deleted_events(self, house):
		events = Event.objects.deleted_events().filter(house=house).order_by('start')
		return events
