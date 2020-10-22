
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

from postcards.forms import PostcardOrderForm, PostCardBusinessOrderFormStepOne
from postcards.models import PostCard, PostCardOrder, PromoCode
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
                    self.send_confirmation_email(postcard_order)

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
                    json_data["message"] = f"Hi {postcard_order.name}! We wanted to give a big thank you\rfor supporting us. We hope you enjoyed using our postcard service\rand we were able to help make your loved one feel special.\rThere is nothing like receiving personal messages\rthrough the mail! You can check our new collection\rof postcards for Fall 2020 on our site!\r\rLove, Arqam house team"
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



    def send_confirmation_email(self, postcard_order):
        # Compose Email
        
        context = {}

        if postcard_order.finished_image:
            s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
                                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            response = s3_client.generate_presigned_url('get_object', Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': postcard_order.finished_image_path}, ExpiresIn=360000)

            context["image_url"] = response

        subject = f"Your postcard is on it's way."
        context["postcard_order"] = postcard_order
        

        html_content = render_to_string('emails/postcard_shipped_confirmation.html', context)

        text_content = strip_tags(html_content)
        from_email = f'Arqam House <info@arqamhouse.com>'
        to = [postcard_order.email]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()

        return "Done"




class PostCardBusinessOrderViewStepOne(FormView):
    model = PostCard
    template_name = "postcards/business_order_step_one.html"

    def get(self, request, *args, **kwargs):

        data = request.GET
        form = PostCardBusinessOrderFormStepOne()
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        get_data = self.request.GET

        context["form"] = form
        return context




class PostCardBusinessListView(View):
    template_name = "postcards/business_list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        postcards = PostCard.objects.filter(hidden=False)

        get_data = self.request.GET
        if 'success' in get_data:
            context["show_confetti"] = True
            context["postcard_order"] = PostCardOrder.objects.all(
            ).reverse().first()

        context["postcards"] = postcards
        return context





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





def stripePayment(request):
    json_data = json.loads(request.body)
    if json_data:
        print(json_data)
        postcard_id = json_data['postcard']
        quantity = int(json_data['quantity'])
        code = json_data['promo_code']

        postcard = PostCard.objects.get(id=postcard_id)
        print(postcard)

        reduction = 0
        code_used = False
        if code:
            try:
                promo_code = PromoCode.objects.get(code=code.lower())
                reduction = promo_code.fixed_amount
                code_used = True
            except Exception as e:
                print(e)
                reduction = 0
                return JsonResponse({'retry': True})

        if reduction != 0:
            total = int(((postcard.amount - reduction) * quantity) * 100)
            total_decimal = (postcard.amount - reduction) * quantity
        else:
            total = int((postcard.amount * quantity) * 100)
            total_decimal= postcard.amount * quantity
        print(total)

        if total <= 0:
            no_payment = True

            return JsonResponse({'retry': False, 'total': total, 'postcard_name': postcard.name,
                                 'total_decimal': total_decimal, 'code_used': code_used, 'no_payment': no_payment})

        else:
            no_payment = False
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            postcard_intent = stripe.PaymentIntent.create(
                amount=total,
                currency='cad',
                description = "Postcard Arqam House",
                metadata = {
                    'postcard': postcard.name,
                    'postcard_amount': postcard.amount,
                    },
                statement_descriptor="Postcard Arqam House",
            )

            intent_id = postcard_intent.id
            client_secret = postcard_intent.client_secret
            public_key = settings.STRIPE_PUBLIC_KEY

        return JsonResponse({'retry': False, 'total': total, 'intent_id': intent_id, 'client_secret': client_secret, 'public_key': public_key, 'postcard_name': postcard.name,
                             'total_decimal': total_decimal, 'code_used': code_used, 'no_payment': no_payment})


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
            
        try:
            last_postcard = PostCardOrder.objects.filter(post_card=postcard).order_by("-created_at").first()
            days_since_sold = datetime.today().day - last_postcard.created_at.day
            context["last_postcard"] = last_postcard
            context["days_since_sold"] = days_since_sold
        except:
            pass

        context["quantity_str"] = quantity
        postcard_amount = (5*quantity)
        quantity = range(quantity)
        context["one"] = one
        context["quantity"] = quantity
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
    
        # Get buyer name and email address
        name = form.cleaned_data.get('name')
        if len(name) > 30:
            form.add_error(None, "Please keep your name under 30 characters long. Sorry :(")
            return self.render_to_response(self.get_context_data(form=form))

        email = form.cleaned_data.get('email')
        if len(email) > 300:
            form.add_error(None, "Please keep your email under 300 characters long. Sorry :(")
            return self.render_to_response(self.get_context_data(form=form))

        anonymous = form.cleaned_data.get('anonymous')

        street_number = form.cleaned_data.get("street_number")
        if len(street_number) > 20:
            form.add_error(None, "Please keep your street number under 20 characters long. Sorry :(")
            return self.render_to_response(self.get_context_data(form=form))

        route = form.cleaned_data.get("route")
        if len(route) > 100:
            form.add_error(None, "Please keep your route under 100 characters long. Sorry :(")
            return self.render_to_response(self.get_context_data(form=form))

        locality = form.cleaned_data.get("locality")
        if len(locality) > 100:
            form.add_error(None, "Please keep your locality under 100 characters long. Sorry :(")
            return self.render_to_response(self.get_context_data(form=form))

        administrative_area_level_1 = form.cleaned_data.get("administrative_area_level_1")
        if len(administrative_area_level_1) >= 4:
            form.add_error(None, "Please use a 2 digit province code i.e. 'ON'.")
            return self.render_to_response(self.get_context_data(form=form))

        address = form.cleaned_data.get("address")
        if len(address) > 200:
            form.add_error(None, "Please keep the address under 200 characters long.")
            return self.render_to_response(self.get_context_data(form=form))

        postal_code = form.cleaned_data.get("postal_code")
        if len(postal_code) > 10:
            form.add_error(None, "Please keep the postal code under 10 characters long.")
            return self.render_to_response(self.get_context_data(form=form))

        code = form.cleaned_data.get("promo_code")
        try:
            promo_code = PromoCode.objects.get(code=code)
            amount = postcard.amount - promo_code.fixed_amount
        except Exception as e:
            promo_code = None
            amount = postcard.amount * quantity

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

        if amount <= 0:
            pass
        else:
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
        
        except Exception as e:
            print(e)
            form.add_error(None, "Your payment was not processed. A network error prevented payment processing, please try again later.")
            return self.render_to_response(self.get_context_data(form=form))


        postcard_orders = []

        for x in range(quantity):

            recipient_name = form.cleaned_data.get(f"{x}_recipient_name")
            if len(recipient_name) > 30:
                form.add_error(None, f"Please keep recipient {x}'s name under 30 characters long.")
                return self.render_to_response(self.get_context_data(form=form))

            recipient_address = form.cleaned_data.get(f"autocomplete{x}")
            if len(recipient_address) > 200:
                form.add_error(None, f"Please keep recipient {x}'s address under 200 characters long.")
                return self.render_to_response(self.get_context_data(form=form))

            recipient_street_number = form.cleaned_data.get(f"street_number_{x}")
            if len(recipient_street_number) > 20:
                form.add_error(None, f"Please keep recipient {x}'s street number under 20 characters long. Sorry :(")
                return self.render_to_response(self.get_context_data(form=form))

            recipient_route = form.cleaned_data.get(f"route_{x}")
            if len(recipient_route) > 100:
                form.add_error(None, f"Please keep recipient {x}'s route under 100 characters long. Sorry :(")
                return self.render_to_response(self.get_context_data(form=form))

            recipient_locality = form.cleaned_data.get(f"locality_{x}")
            if len(recipient_locality) > 100:
                form.add_error(None, f"Please keep recipient {x}'s locality under 100 characters long. Sorry :(")
                return self.render_to_response(self.get_context_data(form=form))

            recipient_administrative_area_level_1 = form.cleaned_data.get(f"administrative_area_level_1_{x}")
            if len(recipient_administrative_area_level_1) >= 4:
                form.add_error(None, f"Please use a 2 digit province code i.e. 'ON' for recipient {x}.")
                return self.render_to_response(self.get_context_data(form=form))

            recipient_postal_code = form.cleaned_data.get(f"postal_code_{x}")
            if len(recipient_postal_code) > 10:
                form.add_error(None, f"Please keep recipient {x}'s postal code under 10 characters long.")
                return self.render_to_response(self.get_context_data(form=form))

            message_to_recipient = form.cleaned_data.get(f"{x}_message_to_recipient")

            postcard_order = PostCardOrder.objects.create(post_card=postcard, name=name, email=email, anonymous=anonymous, postal_code=postal_code, address=address, 
                                                          street_number=street_number,  message_to_recipient=message_to_recipient, route=route, locality=locality, administrative_area_level_1=administrative_area_level_1,
                                                          recipient_name=recipient_name, recipient_address=recipient_address, recipient_street_number=recipient_street_number,
                                                          recipient_route=recipient_route, recipient_locality=recipient_locality, recipient_administrative_area_level_1=recipient_administrative_area_level_1,
                                                          recipient_postal_code=recipient_postal_code,amount=amount,
                                                          promo_code=promo_code)

            if amount <= 0:
                pass
            else:
                charge = stripe.PaymentIntent.retrieve(stripe_token)
                postcard_order.payment_intent_id = charge['id']
                postcard_order.payment_method_id = charge['payment_method']
                postcard_order.save()
            
            postcard_orders.append(postcard_order)
        
        if promo_code != None:
            promo_code.used += quantity
            promo_code.save()


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
        
        
        valid_data = super(PostCardOrderView, self).form_valid(form)
        return valid_data


    def form_invalid(self, form, request):
        print(form.errors)
        
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
