
from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Organization, OrganizationUser
from profiles.models import Profile, SelectedOrganization
from events.models import Event



class OrganizationAccountMixin(LoginRequiredMixin, object):
	selected_organization_account = None
	organization = None
	profile = None


	def get_organization(self):
		user = self.request.user
		selected_organization = SelectedOrganization.objects.get(user=user)
		organization = selected_organization.organization
		return organization


	def get_profile(self):
		# Get user 
		user = self.request.user

		try:
			profile = Profile.objects.get(user=user)
			self.profile = profile
			return profile
		except:
			return None


	def get_events(self):
		organization = self.get_organization()
		events = Event.objects.active_events().filter(organization=organization)
		return events
		



class OrganizationLandingMixin(object):
	organization = None
	users = None
	profiles = None

	def get_organization(self, slug):
		try:
			organization = Organization.objects.get(slug=slug)
			self.organization = organization
			return organization
		except:
			return None

	def get_users(self, organization):
		users = []
		organization_users = OrganizationUser.objects.filter(organization=organization)
		for organization_user in organization_users:
			users.append(organization_user.user)
		self.users = users
		return users

	def get_profiles(self, users):
		profiles = []
		for user in users:
			profile = Profile.objects.get(user=user)
			profiles.append(profile)
		self.profiles = profiles
		return profiles











