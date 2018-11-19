
from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Organization, OrganizationUser, SelectedUserOrganization
from profiles.models import Profile
from events.models import Event



class OrganizationAccountMixin(LoginRequiredMixin, object):
	selected_organization_account = None
	organization = None
	profile = None


	def get_organization(self):
		# Get user 
		user = self.request.user
		# Find which organization is selected by the user 
		selected_organization_account = SelectedUserOrganization.objects.filter(user=user)
		# Make sure it exits
		if selected_organization_account.exists() and selected_organization_account.count() == 1:
			self.selected_organization_account = selected_organization_account.first()
			self.organization = selected_organization_account.first().organization
			return selected_organization_account.first().organization
		return None


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
		events = Event.objects.active_events(organization=organization)
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











