import json
import stripe
import decimal
from django.utils import timezone
from django.utils.timezone import datetime, timedelta
from django.conf import settings
from django.db.models import Q
from django.core import serializers
from django.template.loader import render_to_string
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views import View
from django.urls import reverse
from django.contrib import messages

from django.core.mail import send_mail, EmailMultiAlternatives

from weasyprint import HTML, CSS
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from itertools import chain
from operator import attrgetter

from houses.mixins import HouseAccountMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from donations.forms import DonationForm

from houses.models import House
from subscribers.models import Subscriber
from profiles.models import Profile
from donations.models import Donation, DonationType
from donations.forms import DonationTypeForm
from payments.models import Transaction


# Create your views here.
class DonationPublicListView(View):
    template_name = "donations/public-list.html"

    def get(self, request, *args, **kwargs):

        house = self.get_house()

        if not house.allow_donations:
            view_name = "home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))

        return render(request, self.template_name, self.get_context_data())


    def graph_data(self, house):
        
        transactions = Transaction.objects.filter(house=house, donation_transaction=True)
        today = timezone.now()
        days_earlier = today - timedelta(days=10)
        day_label = []
        sales_label = []
        total = 0

        for x in range(10):
            one_day_earlier = today - timedelta(days=x)
            transactions_for_day = transactions.filter(created_at__day=one_day_earlier.day, created_at__month=one_day_earlier.month, created_at__year=one_day_earlier.year)

            sales_sum = 0
            for transaction in transactions_for_day:
                if transaction.house_amount:
                    sales_sum += transaction.house_amount
                else:
                    sales_sum += decimal.Decimal(0.00)

            sales_label.append('{0:.2f}'.format(sales_sum))
            day_label.append("%s" % (one_day_earlier.day))

            total += sales_sum
        
        sales_label = list(reversed(sales_label))
        day_label = list(reversed(day_label))

        graph_data = {'sales_label':sales_label, 'day_label':day_label, 'total': total}
        return graph_data

    def get_house(self):
        try:
            house = House.objects.get(slug=self.kwargs['slug'])
            return house
        except Exception as e:
            print(e)
            raise Http404

    def get_context_data(self, *args, **kwargs):
        context = {}
        slug = self.kwargs['slug']
        house = self.get_house()

        donations = Donation.objects.filter(donation_type__house=house).order_by('-created_at')[:30]
        graph_data = self.graph_data(house)
        context["graph_data"] = graph_data

        context["donations"] = donations
        context["house"] = house
        return context







class DonationView(FormView):
    model = Donation
    template_name = "donations/donate.html"

    def get(self, request, *args, **kwargs):
        house = self.get_house()

        if not house.allow_donations:
            view_name = "home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))

        form = DonationForm(house=house)
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "public_donations"
        return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        request = self.request
        slug = self.kwargs['slug']
        house = self.get_house()
        donation_types = DonationType.objects.filter(house=house, deleted=False)
        
        context['donation_types'] = donation_types
        context["form"] = form
        context["house"]= house
        context["public_key"] = settings.STRIPE_PUBLIC_KEY
        return context

    def get_house(self):
        try:
            house = House.objects.get(slug=self.kwargs['slug'])
            return house
        except Exception as e:
            print(e)
            raise Http404

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        house = self.get_house()
        form = DonationForm(house=house, data=data)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)


    def get_charge_descriptor(self, house):
        house_title = ''.join(e for e in house.name if e.isalnum())
        house_title = "Donate AH*%s" % (house_title)
        if len(house_title) > 20:
            descriptor = house_title[:21]
        else:
            descriptor = house_title
        return descriptor

        
    def form_valid(self, form, request):
        data = request.POST
        house = self.get_house()

        stripe_token = data["stripeToken"]
        
        # Get buyer name and email address
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        amount = form.cleaned_data.get('amount')
        donation_type = form.cleaned_data.get('donation_type')
        message = form.cleaned_data.get('message')
        anonymous = form.cleaned_data.get('anonymous')

        if donation_type.collect_address:
            address = form.cleaned_data.get("address")
            postal_code = form.cleaned_data.get("postal_code")
        else:
            address = None
            postal_code = None


        stripe.api_key = settings.STRIPE_SECRET_KEY

        # ====================== Create Arqam House Profile and Subscribe them to the house ===========================
        # Check if user exists in the system 
        email = email.lower()

        try:
            profile = Profile.objects.get(email=email)
            account_created = False

        # If the user doesn't exist at all then we need to create a customer
        except:
            profile_temp_password = get_random_string(length=10)
            profile = Profile.objects.create_user(name=name, email=email, password=profile_temp_password, temp_password=profile_temp_password)
            account_created = True


        # Try for subscriber
        # Either they are already a subscriber 
        try:
            subscriber = Subscriber.objects.get(profile=profile, house=house)

        # Or we need to create a subscriber
        except Exception as e:
            print(e)
            subscriber = Subscriber.objects.create(profile=profile, house=house, events_total=1, attendance_total=1, campaigns_total=1, engagement_total=1)



        try:
            stripe_token = data["stripeToken"]
        except Exception as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)

        stripe_fee = decimal.Decimal(settings.STRIPE_FEE/100)
        stripe_base_fee = decimal.Decimal(settings.STRIPE_BASE_FEE)

        total_fee = (amount * platform_fee) + stripe_base_fee
        print(total_fee)

        stripe_amount = (amount * stripe_fee) + stripe_base_fee
        print(stripe_amount)

        arqam_amount = total_fee - stripe_amount
        print(arqam_amount)

        if donation_type.pass_fee:
            house_amount = amount
            charge_amount = amount + total_fee
            print(house_amount)
            print(charge_amount)
            pass_fee = True

        else:
            house_amount = amount - total_fee
            charge_amount = amount
            print(house_amount)
            print(charge_amount)
            pass_fee = False

        

        try:
            if profile.stripe_customer_id:
                customer = stripe.Customer.retrieve(profile.stripe_customer_id)
            else:
                customer = stripe.Customer.create(source=stripe_token, email=email, name=name)
                print(customer)
                profile.stripe_customer_id = customer.id
                profile.save()

            # Charge the card
            charge = stripe.Charge.create(
                        amount = int(charge_amount * 100),
                        currency = 'cad',
                        description = self.get_charge_descriptor(house),
                        customer = customer.id,
                        metadata = {
                            'transaction_amount': round(charge_amount, 2),
                            'transaction_arqam_amount': round(arqam_amount, 2),
                            'transaction_stripe_amount': round(stripe_amount, 2),
                            'transaction_house_amount': round(house_amount, 2),
                            'buyer_email': email,
                            'buyer_name': name,
                            'house_name': house.name,
                            'house_id': house.id
                            },
                        statement_descriptor = self.get_charge_descriptor(house),
                    )
            
        except stripe.error.CardError as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=forms))
            
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))
        
        except Exception as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        
        transaction = Transaction.objects.create(house=house, name=name, email=email, donation_transaction=True)
        donation = Donation.objects.create(
            donation_type=donation_type, transaction=transaction, name=name, email=email, message=message, address=address, postal_code=postal_code, pass_fee=pass_fee,
            anonymous=anonymous)

        transaction.amount = charge_amount
        transaction.arqam_amount = arqam_amount
        transaction.stripe_amount = stripe_amount
        transaction.house_amount = house_amount
        transaction.payment_id = charge['id']
        transaction.last_four = charge.source['last4']
        transaction.brand = charge.source['brand']
        transaction.network_status = charge.outcome['network_status']
        transaction.risk_level = charge.outcome['risk_level']
        transaction.seller_message = charge.outcome['seller_message']
        transaction.outcome_type = charge.outcome['type']
        transaction.address_line_1 = charge.source['address_line1']
        transaction.address_state = charge.source['address_state']
        transaction.address_postal_code = charge.source['address_zip']
        transaction.address_city = charge.source['address_city']
        transaction.address_country = charge.source['address_country']
        transaction.save()

        if donation_type.pass_fee:
            self.send_confirmation_email(name=name, email=email, house=house, donation_amount=house_amount, covered_fee=True, fee=total_fee)
        else:
            self.send_confirmation_email(name=name, email=email, house=house, donation_amount=charge_amount, covered_fee=False, fee=0.00)

        valid_data = super(DonationView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



    def send_confirmation_email(self, house, donation_amount, name, email, covered_fee, fee):
        # Compose Email
        subject = f'{house.name}: Thank you for your donation, {name}.'
        context = {}
        context["house"] = house
        context["donation_amount"] = donation_amount
        context["covered_fee"] = covered_fee
        context["fee"] = fee
        context["name"] = name
        
        html_content = render_to_string('emails/donation_confirmation.html', context)
        text_content = strip_tags(html_content)
        from_email = f'{house.name} <info@arqamhouse.com>'
        to = [email]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return "Done"





class DonationDetailView(HouseAccountMixin, View):
    template_name = "donations/detail.html"

    def get(self, request, *args, **kwargs):
        house = self.get_house()

        if not house.allow_donations:
            view_name = "donations:dashboard"
            return HttpResponseRedirect(reverse(view_name))

        return render(request, self.template_name, self.get_context_data())

    def get_donation(self):
        public_id = self.kwargs["public_id"]
        try:
            donation = Donation.objects.get(public_id=public_id)
            return donation
        except Exception as e:
            print(e)
            return Http404

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        donation = self.get_donation()
        total_fee = donation.transaction.stripe_amount + donation.transaction.arqam_amount

        context["house"] = house
        context["donation"] = donation
        context["total_fee"] = total_fee
        context["donation_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context








class DonationDashboardView(HouseAccountMixin, View):
    template_name = "donations/dashboard.html"


    def graph_data(self, house):
        
        transactions = Transaction.objects.filter(house=house, donation_transaction=True)
        today = timezone.now()
        days_earlier = today - timedelta(days=10)
        day_label = []
        sales_label = []
        total = 0

        for x in range(10):
            one_day_earlier = today - timedelta(days=x)
            transactions_for_day = transactions.filter(created_at__day=one_day_earlier.day, created_at__month=one_day_earlier.month, created_at__year=one_day_earlier.year)

            sales_sum = 0
            for transaction in transactions_for_day:
                if transaction.house_amount:
                    sales_sum += transaction.house_amount
                else:
                    sales_sum += decimal.Decimal(0.00)

            sales_label.append('{0:.2f}'.format(sales_sum))
            day_label.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))

            total += sales_sum
        
        sales_label = list(reversed(sales_label))
        day_label = list(reversed(day_label))

        graph_data = {'sales_label':sales_label, 'day_label':day_label, 'total': total}
        return graph_data


    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    
    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        house = self.get_house()

        if 'stop_donations' in data:
            if data['stop_donations'] == 'true':
                house.allow_donations = False
                messages.warning(request, 'Donations are now stopped.')
            else:
                house.allow_donations = True
                messages.success(request, 'You are now accepting donations')
            house.save()

        view_name = "donations:dashboard"
        return HttpResponseRedirect(reverse(view_name))

    
    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        donations = Donation.objects.filter(donation_type__house=house).order_by('-created_at')
        graph_data = self.graph_data(house)

        context["graph_data"] = graph_data
        context["house"] = house
        context["donations"] = donations
        context["donation_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context







class DonationListView(HouseAccountMixin, ListView):
    model = Donation
    template_name = "donations/list.html"


    def get(self, request, *args, **kwargs):
        house = self.get_house()
        if not house.allow_donations:
            view_name = "donations:dashboard"
            return HttpResponseRedirect(reverse(view_name))
        return render(request, self.template_name, self.get_context_data())


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        house = self.get_house()

        if 'allow_donation' in data:
            house.allow_donations = True
            house.save()

            donation_type = DonationType.objects.create(house=house, name="General Donation", general_donation=True, pass_fee=False)


        all_donations = Donation.objects.filter(donation_type__house=house).order_by('-created_at')
        search_terms = data["search"].split()

        if data["search"] == '':
            donations = all_donations
        else:
            counter = 0
            for search_term in search_terms:
                if counter == 0:
                    donations = all_donations.filter(Q(name__icontains=search_term) | Q(
                        transaction__amount__icontains=search_term) | Q(email__icontains=search_term) | Q(donation_type__name__icontains=search_term))
                else:
                    donations = donations.filter(Q(name__icontains=search_term) | Q(
                        transaction__amount__icontains=search_term) | Q(email__icontains=search_term) | Q(donation_type__name__icontains=search_term))
                print(counter)
                counter += 1
        
        donations = donations[:100]
        html = render_to_string('donations/donations-dynamic-table-body.html', {'donations': donations})
        return HttpResponse(html)

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        donations = Donation.objects.filter(donation_type__house=house).order_by('-created_at')
        
        context["house"] = house
        context["donations"] = donations
        context["donation_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context










class DonationTypeListView(HouseAccountMixin, ListView):
    model = DonationType
    template_name = "donations/types.html"


    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        donation_types = DonationType.objects.filter(house=house, deleted=False)
        
        context["house"] = house
        context["donation_types"] = donation_types
        context["donation_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context




class DonationTypeCreateView(HouseAccountMixin, CreateView):
    model = DonationType
    template_name = "donations/type.html"

    def get_success_url(self):
        view_name = "donations:types"
        return reverse(view_name)

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["donation_tab"] = True
        return context


    def get(self, request, *args, **kwargs):
        self.object = None
        form = DonationTypeForm()
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = None
        data = request.POST
        house = self.get_house()
        form = DonationTypeForm(data=data)
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        house = self.get_house()
        form.instance.house = house
        self.object = form.save()

        print(form.cleaned_data)

        messages.success(request, 'Donation Type Added!')
        valid_data = super(DonationTypeCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class DonationTypeUpdateView(HouseAccountMixin, UpdateView):
    model = DonationType
    template_name = "donations/type.html"

    def get_success_url(self):
        view_name = "events:resources"
        return reverse(view_name, kwargs={"slug": self.kwargs["slug"]})

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["donation_tab"] = True
        return context

    def get_donation_type(self):
        donation_type_id = self.kwargs["pk"]
        try:
            donation_type = DonationType.objects.get(id=donation_type_id)
            return donation_type
        except Exception as e:
            print(e)
            return Http404


    def get(self, request, *args, **kwargs):
        self.object = self.get_donation_type()
        form = DonationTypeForm(instance=self.object)
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_donation_type()
        data = request.POST
        house = self.get_house()
        form = DonationTypeForm(instance=self.object, data=data)
        if form.is_valid():
            return self.form_valid(form, request, event)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request, event):
        house = self.get_house()
        form.instance.house = house
        self.object = form.save()

        print(form.cleaned_data)

        messages.success(request, 'Donation Type Updated!')
        valid_data = super(DonationTypeUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
