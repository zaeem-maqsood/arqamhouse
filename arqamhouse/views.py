from django.views import View
from django.shortcuts import render, redirect



class HomePageView(View):
	template_name = "frontend/home.html"

	def get(self, request, *args, **kwargs):
		# context = {}
		# context["title"] = "Arqam House"
		# return render(request, self.template_name, context)
		response = redirect('profile/login')
		return response


