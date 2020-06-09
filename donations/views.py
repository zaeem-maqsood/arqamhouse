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

from django.db.models import Sum

from django.core.mail import send_mail, EmailMultiAlternatives

from weasyprint import HTML, CSS
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from itertools import chain
from operator import attrgetter

from houses.mixins import HouseAccountMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from donations.forms import DonationForm, GiftDonationForm

from houses.models import House
from subscribers.models import Subscriber, Audience
from profiles.models import Profile
from donations.models import Donation, DonationType, GiftDonationItem
from donations.forms import DonationTypeForm
from payments.models import Transaction, Refund
from core.mixins import SuperUserRequiredMixin


# Create your views here.
class DonationGiftsSentView(SuperUserRequiredMixin, View):
    template_name = "donations/donation_gifts_sent.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


    def get_context_data(self, *args, **kwargs):
        context = {}
        donation_gifts_not_sent = Donation.objects.filter(sent_to_recipient=False, gift_donation_item__isnull=False).order_by('-created_at')
        context["donation_gifts_not_sent"] = donation_gifts_not_sent
        return context



# Create your views here.
class DonationGiftListView(View):
    template_name = "donations/gift_donations.html"

    def get(self, request, *args, **kwargs):

        house = self.get_house()

        if not house.allow_donations:
            view_name = "home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))

        return render(request, self.template_name, self.get_context_data())

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

        default_donation_items = GiftDonationItem.objects.filter(default=True)
        gift_donation_items = GiftDonationItem.objects.filter(house=house).order_by('-created_at')

        context["default_donation_items"] = default_donation_items
        context["gift_donation_items"] = gift_donation_items
        context["house"] = house
        return context





class DonationGiftView(FormView):
    model = Donation
    template_name = "donations/donate_gift.html"

    def get(self, request, *args, **kwargs):
        house = self.get_house()

        if not house.allow_donations:
            view_name = "home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))

        form = GiftDonationForm(house=house)
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "public_donations_live"
        return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        request = self.request

        house = self.get_house()
        gift_donation_item = self.get_gift_donation_item()
        donation_types = DonationType.objects.filter(house=house, deleted=False)
        
        context["gift_donation_item"] = gift_donation_item
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

    def get_gift_donation_item(self):
        try:
            gift_donation_item = GiftDonationItem.objects.get(id=self.kwargs['pk'])
            return gift_donation_item
        except Exception as e:
            print(e)
            raise Http404


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        house = self.get_house()
        form = GiftDonationForm(house=house, data=data)

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

        recipient_name = form.cleaned_data.get('recipient_name')
        recipient_email = form.cleaned_data.get('recipient_email')
        recipient_address = form.cleaned_data.get('recipient_address')
        recipient_postal_code = form.cleaned_data.get('recipient_postal_code')
        send_e_card = form.cleaned_data.get('send_e_card')


        if donation_type.collect_address:
            address = form.cleaned_data.get("address")
        else:
            address = None


        stripe.api_key = settings.STRIPE_SECRET_KEY

        # ====================== Create Arqam House Profile and Subscribe them to the house ===========================
        # Check if user exists in the system 
        email = email.lower()

        gift_donation_item = self.get_gift_donation_item()

        platform_fee = decimal.Decimal(settings.PLATFORM_FEE/100)

        stripe_fee = decimal.Decimal(settings.STRIPE_FEE/100)
        stripe_base_fee = decimal.Decimal(settings.STRIPE_BASE_FEE)

        total_fee = (amount * platform_fee) + stripe_base_fee
        print(total_fee)

        stripe_amount = (amount * stripe_fee) + stripe_base_fee
        print(stripe_amount)

        arqam_amount = total_fee - stripe_amount + gift_donation_item.amount
        print(arqam_amount)

        if donation_type.pass_fee:
            house_amount = amount
            charge_amount = amount + total_fee + gift_donation_item.amount
            print(house_amount)
            print(charge_amount)
            pass_fee = True
            donation_amount = house_amount

        else:
            house_amount = amount - total_fee
            charge_amount = amount + gift_donation_item.amount
            print(house_amount)
            print(charge_amount)
            pass_fee = False
            donation_amount = amount



        try:
            profile = Profile.objects.get(email=email)
            account_created = False

        # If the user doesn't exist at all then we need to create a customer
        except:
            profile_temp_password = get_random_string(length=10)
            profile = Profile.objects.create_user(
                name=name, email=email, password=profile_temp_password, temp_password=profile_temp_password)
            account_created = True


        # Try for subscriber
        # Either they are already a subscriber 
        try:
            subscriber = Subscriber.objects.get(profile=profile, house=house)
            subscriber.times_donated += 1

        # Or we need to create a subscriber
        except Exception as e:
            print(e)
            subscriber = Subscriber.objects.create(
                profile=profile, house=house, total_events_since_subscribed=0, event_attendance=0, total_campaigns_since_subscribed=0,
                campaign_views=0, times_donated=1)



        try:
            stripe_token = data["stripeToken"]
        except Exception as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        

        

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
                        amount = int(round(charge_amount, 2) * 100),
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
            print(e.error.code)
            print(e.error.message)
            print(e.error.type)
            print(e.error.param)
            error_message = e.error.message
            if e.error.code == "incorrect_zip":
                error_message = "The postal code your provided failed validation. Please make sure your postal code is correct and try again."

            if e.error.code == "card_declined":
                error_message = "The card you provided was declined. Please use another payment method."

            form.add_error("amount", f"{error_message}")
            return self.render_to_response(self.get_context_data(form=form))
            
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

        transaction.amount = charge_amount - gift_donation_item.amount
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

        donation = Donation.objects.create(
            donation_type=donation_type, transaction=transaction, name=name, email=email, message=message, address=address, postal_code=charge.source['address_zip'], pass_fee=pass_fee,
            anonymous=anonymous, amount=donation_amount, recipient_name=recipient_name, recipient_email=recipient_email, recipient_address=recipient_address, recipient_postal_code=recipient_postal_code,
            send_e_card=send_e_card, gift_donation_item=gift_donation_item, gift_donation_item_amount=gift_donation_item.amount)


        subscriber_amount_donated = subscriber.amount_donated
        if subscriber_amount_donated is None:
            subscriber_amount_donated = decimal.Decimal('0.00')
        subscriber_amount_donated += donation.amount
        subscriber.amount_donated = subscriber_amount_donated
        subscriber.save()

        try:
            audience = Audience.objects.get(house=house, donation_type=donation_type)
            audience.subscribers.add(subscriber)
        except Exception as e:
            print(e)

        if donation_type.pass_fee:
            self.send_confirmation_email(name=name, email=email, house=house, donation_amount=donation_amount, covered_fee=True, fee=total_fee)
        else:
            self.send_confirmation_email(name=name, email=email, house=house, donation_amount=donation_amount, covered_fee=False, fee=0.00)

        valid_data = super(DonationGiftView, self).form_valid(form)
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
        
        donations = Donation.objects.filter(donation_type__house=house)
        today = timezone.now()
        days_earlier = today - timedelta(days=10)
        day_label = []
        sales_label = []
        total = 0

        for x in range(10):
            one_day_earlier = today - timedelta(days=x)
            
            donations_for_day = donations.filter(transaction__created_at__day=one_day_earlier.day,
                                                 transaction__created_at__month=one_day_earlier.month, transaction__created_at__year=one_day_earlier.year)
    
            sales_sum = 0
            for donation in donations_for_day:
                sales_sum += donation.amount
                

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

        donations = Donation.objects.filter(donation_type__house=house).order_by('-created_at')[:50]
        graph_data = self.graph_data(house)
        context["graph_data"] = graph_data

        context["donations"] = donations
        context["house"] = house
        return context







class DonationPublicListLiveView(View):
    template_name = "donations/public-list-live.html"

    def get(self, request, *args, **kwargs):

        house = self.get_house()
        if not house.allow_donations:
            view_name = "home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))

        return render(request, self.template_name, self.get_context_data())

    def graph_data(self, house):
        from django.utils.timezone import localdate
        donations = Donation.objects.filter(donation_type__house=house)
        this_minute = timezone.localtime(timezone.now())
        minute_label = []
        sales_label = []
        total = 0

        donations_for_day = donations.filter(transaction__created_at__day=this_minute.day, transaction__created_at__month=this_minute.month,
                                             transaction__created_at__year=this_minute.year).aggregate(Sum('amount'))
        
        total = donations_for_day["amount__sum"]
        if not total:
            total = 0

        for x in range(10):
            ten_minutes_earlier = this_minute - timedelta(minutes=x)
            donations_for_ten_minutes = donations.filter(transaction__created_at__minute=ten_minutes_earlier.minute,
                                                         transaction__created_at__hour=ten_minutes_earlier.hour, transaction__created_at__day=ten_minutes_earlier.day,
                                                         transaction__created_at__month=ten_minutes_earlier.month, transaction__created_at__year=ten_minutes_earlier.year)
            print(donations_for_ten_minutes)
            sales_sum = 0
            for donation in donations_for_ten_minutes:
                sales_sum += donation.amount

            sales_label.append('{0:.2f}'.format(sales_sum))
            # minute_label.append("%s:%s" % (ten_minutes_earlier.hour, ten_minutes_earlier.minute))
            minute_label.append(ten_minutes_earlier.strftime("%I:%M"))


        sales_label = list(reversed(sales_label))
        minute_label = list(reversed(minute_label))

        graph_data = {'sales_label': sales_label,
                      'minute_label': minute_label, 'total': total}
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

        this_minute = timezone.localtime(timezone.now())
        donations = Donation.objects.filter(donation_type__house=house, transaction__created_at__day=this_minute.day, transaction__created_at__month=this_minute.month,
                                            transaction__created_at__year=this_minute.year)

        total_donations = donations.aggregate(Sum('amount'))["amount__sum"]

        graph_data = self.graph_data(house)
        context["graph_data"] = graph_data

        context["donations"] = donations
        context["house"] = house
        return context


    def post(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        house = self.get_house()
        graph_data = self.graph_data(house)
        print(graph_data)
        this_minute = timezone.localtime(timezone.now())
        donations = Donation.objects.filter(donation_type__house=house, transaction__created_at__day=this_minute.day, transaction__created_at__month=this_minute.month,
                         transaction__created_at__year=this_minute.year)

        total_donations = donations.aggregate(Sum('amount'))["amount__sum"]
        if not total_donations:
            total_donations = 0.00

        html = render_to_string('donations/public-list-live-dynamic-body.html', {'donations': donations})
        graph_data["html"] = html
        graph_data["total_donations"] = total_donations

        json_data = json.loads(request.body)
        if json_data:
            print(json_data)
            
            return JsonResponse(graph_data)








class DonationView(FormView):
    model = Donation
    template_name = "donations/donate.html"

    def get(self, request, *args, **kwargs):
        house = self.get_house()

        data = request.GET
        initial_data = {}

        # See if there is a donation type in the get parameter
        # If there is make sure its valid
        if 'type' in data:
            try:
                donation_type = DonationType.objects.get(id=data["type"], deleted=False)
                initial_data["donation_type"] = donation_type
            except Exception as e:
                print(e)

            
        if 'amount' in data:
            try:
                initial_data["amount"] = decimal.Decimal(data["amount"])
            except Exception as e:
                print(e)

        if not house.allow_donations:
            view_name = "home_page"
            return HttpResponseRedirect(reverse(view_name, kwargs={"slug": house.slug}))

        form = DonationForm(house=house, initial=initial_data)
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "public_donations_live"
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
        else:
            address = None


        stripe.api_key = settings.STRIPE_SECRET_KEY

        # ====================== Create Arqam House Profile and Subscribe them to the house ===========================
        # Check if user exists in the system 
        email = email.lower()



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
            donation_amount = house_amount

        else:
            house_amount = amount - total_fee
            charge_amount = amount
            print(house_amount)
            print(charge_amount)
            pass_fee = False
            donation_amount = charge_amount



        try:
            profile = Profile.objects.get(email=email)
            account_created = False

        # If the user doesn't exist at all then we need to create a customer
        except:
            profile_temp_password = get_random_string(length=10)
            profile = Profile.objects.create_user(
                name=name, email=email, password=profile_temp_password, temp_password=profile_temp_password)
            account_created = True


        # Try for subscriber
        # Either they are already a subscriber 
        try:
            subscriber = Subscriber.objects.get(profile=profile, house=house)
            subscriber.times_donated += 1

        # Or we need to create a subscriber
        except Exception as e:
            print(e)
            subscriber = Subscriber.objects.create(
                profile=profile, house=house, total_events_since_subscribed=0, event_attendance=0, total_campaigns_since_subscribed=0,
                campaign_views=0, times_donated=1)



        try:
            stripe_token = data["stripeToken"]
        except Exception as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))

        

        

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
                        amount = int(round(charge_amount, 2) * 100),
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
            print(e.error.code)
            print(e.error.message)
            print(e.error.type)
            print(e.error.param)
            error_message = e.error.message
            if e.error.code == "incorrect_zip":
                error_message = "The postal code your provided failed validation. Please make sure your postal code is correct and try again."

            if e.error.code == "card_declined":
                error_message = "The card you provided was declined. Please use another payment method."

            form.add_error("amount", f"{error_message}")
            return self.render_to_response(self.get_context_data(form=form))
            
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

        donation = Donation.objects.create(
            donation_type=donation_type, transaction=transaction, name=name, email=email, message=message, address=address, postal_code=charge.source['address_zip'], pass_fee=pass_fee,
            anonymous=anonymous, amount=donation_amount)


        subscriber_amount_donated = subscriber.amount_donated
        if subscriber_amount_donated is None:
            subscriber_amount_donated = decimal.Decimal('0.00')
        subscriber_amount_donated += donation.amount
        subscriber.amount_donated = subscriber_amount_donated
        subscriber.save()

        try:
            audience = Audience.objects.get(house=house, donation_type=donation_type)
            audience.subscribers.add(subscriber)
        except Exception as e:
            print(e)

        if donation_type.pass_fee:
            self.send_confirmation_email(name=name, email=email, house=house, donation_amount=donation_amount, covered_fee=True, fee=total_fee)
        else:
            self.send_confirmation_email(name=name, email=email, house=house, donation_amount=donation_amount, covered_fee=False, fee=0.00)

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
        
        if donation.gift_donation_item:
            total_charged = donation.transaction.amount + donation.gift_donation_item_amount
            total_fee = donation.transaction.stripe_amount + \
                donation.transaction.arqam_amount - donation.gift_donation_item_amount
        else:
            total_charged = donation.transaction.amount
            total_fee = donation.transaction.stripe_amount + donation.transaction.arqam_amount

        context["house"] = house
        context["donation"] = donation
        context["total_fee"] = total_fee
        context["total_charged"] = total_charged
        context["donation_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        house = self.get_house()
        donation = self.get_donation()

        if 'refund' in data:
            refund = Refund.objects.create(transaction=donation.transaction, amount=donation.transaction.amount, house_amount=donation.transaction.house_amount, donation_refund=True)
            stripe.api_key = settings.STRIPE_SECRET_KEY
            response = stripe.Refund.create(charge=donation.transaction.payment_id, amount=int(donation.transaction.amount*100))
            print("It is coming here")
            print(response)
            messages.success(request, "Refund Sent!")
            donation.refunded = True
            donation.refund_reason = "Refunded by house."
            donation.refund = refund
            donation.save()

            subscriber = Subscriber.objects.get(profile__email=donation.email, house=house)
            subscriber.times_donated -= 1
            subscriber.amount_donated = subscriber.amount_donated - donation.amount
            subscriber.save()

        return render(request, self.template_name, self.get_context_data())








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
                general_donation_type = DonationType.objects.filter(house=house, general_donation=True)
                if not general_donation_type:
                    general_donation_type = DonationType.objects.create(house=house, general_donation=True, name="General Donation")
                
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
        context["dashboard_events"] = self.get_events()
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

        audience = Audience.objects.create(house=house, name=self.object.name, donation_type=self.object)

        valid_data = super(DonationTypeCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class DonationTypeUpdateView(HouseAccountMixin, UpdateView):
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
        context["update"] = True
        context["dashboard_events"] = self.get_events()
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
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
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
