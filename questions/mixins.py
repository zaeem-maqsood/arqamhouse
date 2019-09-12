from core.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from houses.models import House, HouseUser
from profiles.models import Profile
from .models import Question


class QuestionSecurityMixin(object):

	def test_func(self):
		house_users = HouseUser.objects.filter(profile=self.request.user)
		question = Question.objects.get(id=self.kwargs['pk'])
		print(question)
		for house_user in house_users:
			if question.house == house_user.house:
				return True
		return False