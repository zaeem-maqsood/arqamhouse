
import json
import stripe
import decimal
import sendgrid
import textwrap
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

from urllib.parse import unquote
import boto3
from botocore.client import Config

from itertools import chain
from operator import attrgetter

from houses.mixins import HouseAccountMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from postcards.forms import PostcardOrderForm
from postcards.models import PostCard, PostCardOrder
from profiles.models import Profile

from core.mixins import SuperUserRequiredMixin

# Create your views here.


class PostCardManageOrdersView(View, SuperUserRequiredMixin):

    template_name = "postcards/manage.html"

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        get_data = self.request.GET

        if 'show_all' in get_data:
            postcard_orders = PostCardOrder.objects.all()
        else:
            postcard_orders = PostCardOrder.objects.filter(sent_to_recipient=False).order_by("created_at")

        context["orders"] = postcard_orders
        return context


    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        json_list = []

        if 'sent' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "sent":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    postcard_order.sent_to_recipient = True
                    postcard_order.envelope_printed = True
                    postcard_order.front_printed = True
                    postcard_order.message_printed = True
                    postcard_order.name_printed = True
                    postcard_order.save()

        if 'no_sent' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_sent":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    postcard_order.sent_to_recipient = False
                    postcard_order.save()


        if 'envelope' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "envelope":
                    print(field)
                    postcard_order = PostCardOrder.objects.get(id=field)
                    print(postcard_order)
                    json_data["sender_name"] = postcard_order.name
                    line_1 = f"{postcard_order.street_number} {postcard_order.route}"
                    json_data["sender_line_1"] = line_1
                    postal_code = postcard_order.postal_code.replace(" ", "")
                    cleaned_postal_code = postal_code[:3] + " " + postal_code[3:]
                    line_2 = f"{postcard_order.locality}, {postcard_order.administrative_area_level_1}  {cleaned_postal_code}"
                    json_data["sender_line_2"] = line_2

                    json_data["recipient_name"] = postcard_order.recipient_name
                    line_1 = f"{postcard_order.recipient_street_number} {postcard_order.recipient_route}"
                    json_data["recipient_line_1"] = line_1
                    postal_code = postcard_order.recipient_postal_code.replace(" ", "")
                    cleaned_postal_code = postal_code[:3] + " " + postal_code[3:]
                    line_2 = f"{postcard_order.recipient_locality}, {postcard_order.recipient_administrative_area_level_1}  {cleaned_postal_code}"
                    json_data["recipient_line_2"] = line_2

                    json_list.append(json_data)


        if 'ap_envelope' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_envelope":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["sender_name"] = "Arqam House"
                    json_data["sender_line_1"] = ""
                    json_data["sender_line_2"] = ""
                    json_data["recipient_name"] = postcard_order.name
                    line_1 = f"{postcard_order.street_number} {postcard_order.route}"
                    json_data["recipient_line_1"] = line_1
                    postal_code = postcard_order.postal_code.replace(" ", "")
                    cleaned_postal_code = postal_code[:3] + " " + postal_code[3:]
                    line_2 = f"{postcard_order.locality}, {postcard_order.administrative_area_level_1}  {cleaned_postal_code}"
                    json_data["recipient_line_2"] = line_2

                    json_list.append(json_data)


        if 'no_envelope' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_envelope":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    postcard_order.envelope_printed = False
                    postcard_order.save()


        if 'front' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "front":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["id"] = postcard_order.post_card.id
                    json_list.append(json_data)

                    postcard_order.envelope_printed = True
                    postcard_order.save()


        if 'ap_front' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_front":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["id"] = 6
                    json_list.append(json_data)


        if 'no_front' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_front":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    postcard_order.front_printed = False
                    postcard_order.save()


        if 'message' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "message":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["id"] = postcard_order.post_card.id
                    json_data["message"] = '\n'.join(['\r'.join(textwrap.wrap(line, 60, break_long_words=False, replace_whitespace=False)) for line in postcard_order.message_to_recipient.splitlines() if line.strip() != ''])
                    json_list.append(json_data)

                    postcard_order.envelope_printed = True
                    postcard_order.front_printed = True
                    postcard_order.save()


        if 'ap_message' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_message":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["id"] = 6
                    json_data["message"] = f"Hi {postcard_order.name}! We wanted to give a big thank you\rfor supporting us. We hope you enjoyed using our postcard service\rand we were able to help make your loved one feel special.\rThere is nothing like receiving personal messages\rthrough the mail! You can check our new collection\rof postcards for Fall 2020 on our site!.\r\rLove, Arqam house team"
                    json_list.append(json_data)

        if 'no_message' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_message":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    postcard_order.message_printed = False
                    postcard_order.save()


        if 'name' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "name":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["id"] = postcard_order.post_card.id
                    json_data["name"] = postcard_order.recipient_name
                    json_list.append(json_data)

                    postcard_order.envelope_printed = True
                    postcard_order.front_printed = True
                    postcard_order.message_printed = True
                    postcard_order.save()


        if 'ap_name' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_name":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    json_data["id"] = 6
                    json_data["name"] = postcard_order.name
                    json_list.append(json_data)


        if 'no_name' in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_name":
                    postcard_order = PostCardOrder.objects.get(id=field)
                    postcard_order.name_printed = False
                    postcard_order.save()


        

        
        if json_data:
            return JsonResponse(json_list, safe=False)
                
        
        return render(request, self.template_name, self.get_context_data())
        




class PostCardListView(View):
    template_name = "postcards/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        postcards = PostCard.objects.filter(hidden=False)

        get_data = self.request.GET
        if 'success' in get_data:
            context["show_confetti"] = True
            context["postcard_order"] = PostCardOrder.objects.all().reverse().first()

        context["postcards"] = postcards
        return context





class PostCardOrderView(FormView):
    model = PostCard
    template_name = "postcards/order.html"

    def get(self, request, *args, **kwargs):

        data = request.GET

        if 'quantity' in data:
            quantity = data["quantity"]

        else:
            quantity = 1
    
        initial_data = {}
        form = PostcardOrderForm(quantity)
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_success_url(self):
        view_name = "postcards:list"
        return reverse(view_name) + "?success=true"


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

        data = request.GET
        if 'quantity' in data:
            quantity = int(data["quantity"])
            one = False
        else:
            quantity = 1
            one = True

        postcard = self.get_postcard()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        # postcard_intent_id = request.session.get('postcard_intent_id')
        # if postcard_intent_id:
        #     postcard_intent = stripe.PaymentIntent.create(
        #         postcard_intent_id,
        #         amount=(500 * quantity),
        #         description="Postcard Arqam House",
        #         metadata={
        #             'postcard': postcard.name,
        #             'postcard_amount': postcard.amount,
        #         },
        #         statement_descriptor="Postcard Arqam House",
        #     )

        #     request.session['postcard_intent_id'] = str(postcard_intent.id)
        #     request.session.modified = True

        # else:
        postcard_intent = stripe.PaymentIntent.create(
            amount=(500 * quantity),
            currency='cad',
            description = "Postcard Arqam House",
            metadata = {
                'postcard': postcard.name,
                'postcard_amount': postcard.amount,
                },
            statement_descriptor="Postcard Arqam House",
        )
            # request.session['postcard_intent_id'] = str(postcard_intent.id)
            # request.session.modified = True


        context["quantity_str"] = quantity
        postcard_amount = (5*quantity)
        quantity = range(quantity)
        context["one"] = one
        context["quantity"] = quantity
        context["intent_id"] = postcard_intent.id
        context["client_secret"] = postcard_intent.client_secret
        context["public_key"] = settings.STRIPE_PUBLIC_KEY
        context["form"] = form
        context["postcard"] = postcard
        context["postcard_amount"] = postcard_amount
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        if 'quantity' in data:
            quantity = int(data["quantity"])
        else:
            quantity = 1

        form = PostcardOrderForm(data=data, quantity=quantity)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)

        
    def form_valid(self, form, request):
        data = request.POST

        quantity = int(data["quantity"])

        postcard = self.get_postcard()

        stripe_token = data["intent_id"]
    
        # Get buyer name and email address
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        anonymous = form.cleaned_data.get('anonymous')
        street_number = form.cleaned_data.get("street_number")
        route = form.cleaned_data.get("route")
        locality = form.cleaned_data.get("locality")
        administrative_area_level_1 = form.cleaned_data.get("administrative_area_level_1")
        address = form.cleaned_data.get("address")
        postal_code = form.cleaned_data.get("postal_code")

        # Add sender to sendgrid 
        # -------------------------

        try:
            send_grid_data = {}
            send_grid_data["list_ids"] = ["df17f359-2dd8-45ed-b9e1-bcb63080cf96"]
            contacts = []
            data_dict = {}

            data_dict["email"] = email
            data_dict["first_name"] = name
            data_dict["address_line_1"] = f"{street_number} {route}"
            data_dict["city"] = locality
            data_dict["state_province_region"] = administrative_area_level_1
            data_dict["country"] = "Canada"
            data_dict["postal_code"] = postal_code
            contacts.append(data_dict)
            send_grid_data["contacts"] = contacts
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            response = sg.client.marketing.contacts.put(request_body=send_grid_data)

        except Exception as e:
            print(e)


        # -------------------------


        
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
            form.add_error(None, "Your payment was not processed. A network error prevented payment processing, please try again later.")
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
            form.add_error(None, "Your payment was not processed. A network error prevented payment processing, please try again later.")
            del request.session['intent']
            request.session.modified = True
            return self.render_to_response(self.get_context_data(form=form))


        postcard_orders = []

        for x in range(quantity):
            recipient_name = form.cleaned_data.get(f"{x}_recipient_name")
            recipient_address = form.cleaned_data.get(f"autocomplete{x}")
            recipient_street_number = form.cleaned_data.get(f"street_number_{x}")
            recipient_route = form.cleaned_data.get(f"route_{x}")
            recipient_locality = form.cleaned_data.get(f"locality_{x}")
            recipient_administrative_area_level_1 = form.cleaned_data.get(f"administrative_area_level_1_{x}")
            recipient_postal_code = form.cleaned_data.get(f"postal_code_{x}")
            message_to_recipient = form.cleaned_data.get(f"{x}_message_to_recipient")

            postcard_order = PostCardOrder.objects.create(post_card=postcard, name=name, email=email, anonymous=anonymous, postal_code=postal_code, address=address, 
                                                          street_number=street_number,  message_to_recipient=message_to_recipient, route=route, locality=locality, administrative_area_level_1=administrative_area_level_1,
                                                          recipient_name=recipient_name, recipient_address=recipient_address, recipient_street_number=recipient_street_number,
                                                          recipient_route=recipient_route, recipient_locality=recipient_locality, recipient_administrative_area_level_1=recipient_administrative_area_level_1,
                                                          recipient_postal_code=recipient_postal_code,
                                                          payment_intent_id=charge['id'], payment_method_id=charge['payment_method'], amount=postcard.amount)
            
            postcard_orders.append(postcard_order)


        if settings.DEBUG == False:
            try:
                self.send_text_message(postcard_orders)
            except Exception as e:
                print(e)


        try: 
            self.send_confirmation_email(postcard_orders)
        except Exception as e:
            print(e)


        postcard.amount_sold += 1
        postcard.save()

        # Delete the session intent variable 
        del request.session['postcard_intent_id']
        request.session.modified = True
        valid_data = super(PostCardOrderView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print(form.errors)
        del request.session['postcard_intent_id']
        request.session.modified = True
        return self.render_to_response(self.get_context_data(form=form))


    def send_text_message(self, postcard_orders):
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)

        postcard_amounts = len(postcard_orders)
        sender_name = postcard_orders[0].name
        postcard_type = postcard_orders[0].post_card.name

        if postcard_amounts > 1:
            message = client.messages.create(
                body=f"You have {postcard_amounts} new postcard orders made by {sender_name}, they want the {postcard_type} postcard",
                from_='+16475571902',
                to='+12893887201'
            )
        else:
            postcard_order = postcard_orders[0]
            message = client.messages.create(
                body="You have a new postcard order by %s, they want the %s postcard and they want to send it to %s." % (
                    postcard_order.name, postcard_order.post_card, postcard_order.recipient_name),
                        from_='+16475571902',
                        to='+12893887201'
                    )


    def send_confirmation_email(self, postcard_orders):
        # Compose Email
        
        context = {}

        postcard_amounts = len(postcard_orders)
        postcard_order = postcard_orders[0]
        s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        response = s3_client.generate_presigned_url('get_object', Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': postcard_order.post_card.image_1_path}, ExpiresIn=360000)

        subject = f'Thank you for your purchase, {postcard_order.name}.'
        context["postcard_order"] = postcard_order
        context["image_url"] = response

        if postcard_amounts == 1:
            html_content = render_to_string('emails/postcard_confirmation.html', context)

        else:
            context["postcard_amounts"] = postcard_amounts
            context["postcard_orders"] = postcard_orders
            html_content = render_to_string('emails/postcard_confirmation_multiple.html', context)


        text_content = strip_tags(html_content)
        from_email = f'Arqam House <info@arqamhouse.com>'
        to = [postcard_orders[0].email]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()

        return "Done"
