
from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import House, HouseUser
from profiles.models import Profile
from events.models import Event





class HouseAccountMixin(LoginRequiredMixin, object):
	selected_house_account = None
	house = None
	profile = None

	def test_func(self):
		# house_users = HouseUser.objects.filter(profile=self.request.user)
		pass
		# try:
		# 	event = Event.objects.get(slug=self.kwargs['slug'])
		# 	print(event)
		# 	for house_user in house_users:
		# 		if event.house == house_user.house:
		# 			return True
		# 	return False
		# except:
		# 	pass
			# print("It came her to test")
			# one_to_one_type = self.kwargs['one_to_one_type']
			# one_to_one_id = self.kwargs['one_to_one_id']

			# if one_to_one_type == 'events':
			# 	print("And here")
			# 	event = Event.objects.get(id=one_to_one_id)
			# 	print(event)
			# 	for house_user in house_users:
			# 		if event.house == house_user.house:
			# 			return True
			# 	return False

			# return False




	def get_house(self):
		profile = self.request.user
		house = profile.house
		return house

	def get_profile(self): 
		profile = self.request.user
		return profile

	def get_events(self):
		house = self.get_house()
		events = Event.objects.active_events().filter(house=house)
		return events
		



class HouseLandingMixin(object):
	house = None
	users = None
	profiles = None

	def get_house(self, slug):
		try:
			house = House.objects.get(slug=slug)
			self.house = house
			return house
		except:
			return None

	def get_users(self, house):
		users = []
		house_users = HouseUser.objects.filter(house=house)
		for house_user in house_users:
			users.append(house_user.user)
		self.users = users
		return users

	def get_profiles(self, users):
		profiles = []
		for user in users:
			profile = Profile.objects.get(user=user)
			profiles.append(profile)
		self.profiles = profiles
		return profiles











