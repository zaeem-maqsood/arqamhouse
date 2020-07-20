
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

from twilio.rest import Client

from itertools import chain
from operator import attrgetter

from houses.mixins import HouseAccountMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from postcards.forms import PostcardOrderForm
from postcards.models import PostCard, PostCardOrder
from profiles.models import Profile


# Create your views here.
class PostCardListView(View):
    template_name = "postcards/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        postcards = PostCard.objects.all()
        context["postcards"] = postcards
        return context





class PostCardOrderView(FormView):
    model = PostCard
    template_name = "postcards/order.html"

    def get(self, request, *args, **kwargs):

        data = request.GET
        initial_data = {}
        form = PostcardOrderForm()
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "postcards:list"
        return reverse(view_name)


    def get_postcard(self):
        slug = self.kwargs['slug']
        try:
            postcard = PostCard.objects.get(slug=slug)
            return postcard
        except Exception as e:
            raise Http404


    def get_context_data(self, form, *args, **kwargs):
        context = {}
        request = self.request

        postcard = self.get_postcard()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        postcard_intent_id = request.session.get('postcard_intent_id')
        if postcard_intent_id:
            postcard_intent = stripe.PaymentIntent.retrieve(postcard_intent_id)
        else:
            postcard_intent = stripe.PaymentIntent.create(
                amount=500,
                currency='cad',
                description = "Postcard Arqam House",
                metadata = {
                    'postcard': postcard.name,
                    'postcard_amount': postcard.amount,
                    },
                statement_descriptor="Postcard Arqam House",
            )
            request.session['postcard_intent_id'] = str(postcard_intent.id)
            request.session.modified = True

        context["intent_id"] = postcard_intent.id
        context["client_secret"] = postcard_intent.client_secret
        context["public_key"] = settings.STRIPE_PUBLIC_KEY
        context["form"] = form
        context["postcard"] = postcard
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        form = PostcardOrderForm(data=data)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

        
    def form_valid(self, form, request):
        data = request.POST

        postcard = self.get_postcard()

        stripe_token = data["intent_id"]
    
        # Get buyer name and email address
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        anonymous = form.cleaned_data.get('anonymous')
        address = form.cleaned_data.get("address")
        message_to_recipient = form.cleaned_data.get('message_to_recipient')

        recipient_name = form.cleaned_data.get("recipient_name")
        recipient_email = form.cleaned_data.get("recipient_email")
        recipient_address = form.cleaned_data.get("recipient_address")
        recipient_postal_code = form.cleaned_data.get("recipient_postal_code")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # ====================== Create Arqam House Profile ===========================
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


        try:
            stripe_token = data["intent_id"]
        except Exception as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))


        try:
            if profile.stripe_customer_id:
                customer = stripe.Customer.retrieve(profile.stripe_customer_id)
            else:
                customer = stripe.Customer.create(email=email, name=name)
                print(customer)
                profile.stripe_customer_id = customer.id
                profile.save()

            # Charge the card

            charge = stripe.PaymentIntent.retrieve(stripe_token)
            print("The Charge is \n\n")
            print(charge)
            print("\n\nThe Charge is")
        
        except Exception as e:
            print(e)
            form.add_error("amount", "Your payment was not processed. A network error prevented payment processing, please try again later.")
            del request.session['intent']
            request.session.modified = True
            return self.render_to_response(self.get_context_data(form=form))

        postcard_order = PostCardOrder.objects.create(post_card=postcard,
            name=name, email=email, anonymous=anonymous, address=address, message_to_recipient=message_to_recipient, recipient_name=recipient_name, 
            recipient_address=recipient_address, recipient_postal_code=recipient_postal_code, payment_intent_id=charge['id'], 
            payment_method_id=charge['payment_method'], amount=postcard.amount)


        # if settings.DEBUG == False:
        try:
            self.send_text_message(postcard_order)
        except Exception as e:
            print(e)


        try: 
            self.send_confirmation_email(postcard_order)
        except Exception as e:
            print(e)


        postcard.amount_sold += 1
        postcard.save()

        # Delete the session intent variable 
        del request.session['postcard_intent_id']
        request.session.modified = True
        valid_data = super(PostCardOrderView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        # del request.session['postcard_intent_id']
        # request.session.modified = True
        return self.render_to_response(self.get_context_data(form=form))

    def send_text_message(self, postcard_order):
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="You have a new postcard order by %s, they want the %s postcard and they want to send it to %s." % (
                postcard_order.name, postcard_order.post_card, postcard_order.recipient_name),
                    from_='+16475571902',
                    to='+12893887201'
                )


    def send_confirmation_email(self, postcard_order):
        # Compose Email
        subject = f'Thank you for your purchase, {postcard_order.name}.'
        context = {}
        context["postcard_order"] = postcard_order
        
        html_content = render_to_string('emails/postcard_confirmation.html', context)
        text_content = strip_tags(html_content)
        from_email = f'Arqam House <info@arqamhouse.com>'
        to = [postcard_order.email]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return "Done"
