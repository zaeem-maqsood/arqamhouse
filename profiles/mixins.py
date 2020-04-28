from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from houses.models import House, HouseUser
from profiles.models import Profile


class UpdateProfileMixin(LoginRequiredMixin, object):
    user = None
    House = None
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


    # get the houses the user is associated with
    def get_houses(self, user):
        houses = []
        House_users = HouseUser.objects.filter(user=user)
        for House_user in House_users:
            houses.append(House_user.House)
        return houses


    def does_profile_belong_to_user(self, profile):
        user = self.request.user
        if user == profile.user:
            return True
        else:
            return False



class ProfileMixin(LoginRequiredMixin, object):
    user = None
    House = None
    profile = None

    
    def get_profile(self):

        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None


    # get the houses the user is associated with
    def get_houses(self, user):
        houses = []
        House_users = HouseUser.objects.filter(user=user)
        for House_user in House_users:
            houses.append(House_user.House)
        return houses


    def does_profile_belong_to_user(self, profile):
        user = self.request.user
        if user == profile.user:
            return True
        else:
            return False

