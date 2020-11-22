import json
import stripe
from django.db.models import Q
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction


from .forms import ReportErrorForm
from houses.models import House

from core.mixins import LoginRequiredMixin

from postcards.models import PostCardOrder, PromoCode
from orders.models import Order, LineOrder
from orders.models import PromoCode as orderPromoCode
from recipients.models import Recipient
from profiles.models import Profile, Address

from django.views.decorators.csrf import csrf_exempt



class Menu(LoginRequiredMixin,View):
    template_name = "dashboard/menu.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        profile = self.get_profile()
        context["profile"] = profile
        return render(request, self.template_name, context)


class Dashboard(LoginRequiredMixin,View):
    template_name = "dashboard/main.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        user = request.user
        postcard_orders = LineOrder.objects.filter(order__email=user.email).order_by("-id")[:3]
        context["user"] = user
        context["postcard_orders"] = postcard_orders
        return render(request, self.template_name, context)


class CustomScriptView(View):
    template_name = "custom_script.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        data = request.POST
        print(data)

        # Add logic for actiton 1
        if 'action_1' in data:
            with transaction.atomic():
                addresses = Address.objects.all()
                for address in addresses:
                    address.default = False
                    address.save()

                addresses = Address.objects.all().distinct('profile')
                print(addresses)
                for address in addresses:
                    address.default = True
                    address.save()


        if 'action_2' in data:

            with transaction.atomic():
                pass

        if 'action_3' in data:
            pass

        return render(request, self.template_name, context)





@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(View):

    def post(self, request, *args, **kwargs):

        stripe.api_key = settings.STRIPE_SECRET_KEY

        endpoint_secret = 'whsec_1Ct4Px3Xsh9l23OetcFXBmUxrGBdImOK'

        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        payload = request.body
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object # contains a stripe.PaymentIntent
            print('PaymentIntent was successful!')
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object # contains a stripe.PaymentMethod
            print('PaymentMethod was attached to a Customer!')
        # ... handle other event types
        else:
            # Unexpected event type
            return HttpResponse(status=400)

        return HttpResponse(status=200)


class ApplePayVerificationView(TemplateView):
    template_name = 'static/apple-developer-merchantid-domain-association'





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
    template_name = "frontend/postcard_home.html"

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

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)



class PricingView(View):
    template_name = "frontend/pricing.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)



class ReportErrorView(FormView):

    template_name = "static/report_error.html"
    success_url = "/contact"

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
        email = form.cleaned_data["email"]
        self.send_payout_email(name, message, email)
        messages.success(request, 'Message Sent!')
        valid_data = super(ReportErrorView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))


    def send_payout_email(self, name, message, email):
        subject = 'New Contact Inquiry'
        context = {}
        context["name"] = name
        context["message"] = message
        context["email"] = email
        html_message = render_to_string('emails/error_report.html', context)
        plain_message = strip_tags(html_message)
        from_email = f'Contact Inquiry <{email}>'
        to = ['info@arqamhouse.com']
        mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
        return "Done"
