import json
from django.db.models import Q
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse

from .forms import ReportErrorForm
from houses.models import House

class ApplePayVerificationView(TemplateView):
    template_name = 'static/apple-developer-merchantid-domain-association'


class CustomScriptView(View):
    template_name = "frontend/custom_script.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class FindHouseView(View):
    template_name = "frontend/find_house.html"

    def get(self, request, *args, **kwargs):
        context = {}
        default_house = House.objects.get(slug="arqam-house")
        context["default_house"] = default_house
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        data = request.POST

        json_data = json.loads(request.body)
        if json_data:
            search_terms = json_data["search"].split()
            print(json_data)
            all_houses = None

            if json_data["search"] == '':
                houses = None
            else:
                for search_term in search_terms:
                    houses = House.objects.all().filter(Q(name__icontains=search_term))

            html = render_to_string('frontend/houses-dynamic-body.html', {'houses': houses})
            return JsonResponse({'html': html})



class EventInfoView(View):
    template_name = "frontend/event_info.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)



class DonationInfoView(View):
    template_name = "frontend/donation_info.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class SubscriberInfoView(View):
    template_name = "frontend/subscriber_info.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CampaignInfoView(View):
    template_name = "frontend/campaign_info.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)



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
            context["house"] = house
            return render(request, self.template_name, context)
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
