from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from organizations.models import Organization, OrganizationUser, SelectedUserOrganization
from profiles.models import Profile


class UpdateProfileMixin(LoginRequiredMixin, object):
	user = None
	organization = None
	profile = None


	# Get the profile from the user account
	def get_profile(self, slug):

		try:
			profile = Profile.objects.get(slug=slug)
			self.profile = profile
			return profile
		except:
			return None


	# Get the user account from the slug of the url
	def get_user(self, profile):

		user = profile.user
		return user


	# get the organizations the user is associated with
	def get_organizations(self, user):
		organizations = []
		organization_users = OrganizationUser.objects.filter(user=user)
		for organization_user in organization_users:
			organizations.append(organization_user.organization)
		return organizations


	def does_profile_belong_to_user(self, profile):
		user = self.request.user
		if user == profile.user:
			return True
		else:
			return False



class ProfileMixin(object):
	user = None
	organization = None
	profile = None


	# Get the profile from the user account
	def get_profile(self, slug):

		try:
			profile = Profile.objects.get(slug=slug)
			self.profile = profile
			return profile
		except:
			return None


	# Get the user account from the slug of the url
	def get_user(self, profile):

		user = profile.user
		return user


	# get the organizations the user is associated with
	def get_organizations(self, user):
		organizations = []
		organization_users = OrganizationUser.objects.filter(user=user)
		for organization_user in organization_users:
			organizations.append(organization_user.organization)
		return organizations


	def does_profile_belong_to_user(self, profile):
		user = self.request.user
		if user == profile.user:
			return True
		else:
			return False

