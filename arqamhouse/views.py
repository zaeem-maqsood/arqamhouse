from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

from .forms import ReportErrorForm


class ApplePayVerificationView(TemplateView):
	template_name = 'static/apple-developer-merchantid-domain-association'


class HomePageView(View):
	template_name = "frontend/home.html"

	def get_house(self):
		profile = self.request.user
		house = profile.house
		return house

	def get(self, request, *args, **kwargs):
		context = {}
		try:
			house = self.get_house()
			response = redirect('profile/login')
			return response
		except:
			return render(request, self.template_name, context)



class AboutUsView(View):
	template_name = "frontend/about.html"

	def get_house(self):
		profile = self.request.user
		house = profile.house
		return house

	def get(self, request, *args, **kwargs):
		context = {}
		try:
			house = self.get_house()
			response = redirect('profile/login')
			return response
		except:
			return render(request, self.template_name, context)



class PricingView(View):
	template_name = "frontend/pricing.html"

	def get(self, request, *args, **kwargs):
		context = {}
		return render(request, self.template_name, context)



class ReportErrorView(FormView):

	template_name = "static/report_error.html"
	success_url = "/report"

	def get(self, request, *args, **kwargs):
		context = {}
		profile = request.user
		context["profile"] = profile
		form = ReportErrorForm()
		context["form"] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)
		form = ReportErrorForm(data=data)
		if 'g-recaptcha-response' in data:
			if data['g-recaptcha-response'] == '':
				form.add_error(None, 'Please confirm you are human.')
				return self.form_invalid(form)
			if form.is_valid():
				return self.form_valid(form, request)
			else:
				return self.form_invalid(form)
		else:
			form.add_error(None, 'Please confirm you are human.')
			return self.form_invalid(form)

	def form_valid(self, form, request):
		name = form.cleaned_data["name"]
		message = form.cleaned_data["message"]
		self.send_payout_email(name, message)
		messages.success(request, 'Message Sent!')
		valid_data = super(ReportErrorView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


	def send_payout_email(self, name, message):
		subject = 'New Error Report'
		context = {}
		context["name"] = name
		context["message"] = message
		html_message = render_to_string('emails/error_report.html', context)
		plain_message = strip_tags(html_message)
		from_email = 'Error Manager <admin@arqamhouse.com>'
		to = ['errors@arqamhouse.com']
		mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
		return "Done"
