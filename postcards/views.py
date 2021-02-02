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
from django.contrib.auth import authenticate, login, logout

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

from core.mixins import LoginRequiredMixin

from postcards.forms import PostcardOrderForm, PostCardBusinessOrderFormStepOne
from postcards.models import PostCard, PostCardOrder, NonProfit
from profiles.models import Profile, Address
from orders.models import Order, LineOrder, PromoCode
from recipients.models import Recipient

from core.mixins import SuperUserRequiredMixin

# Create your views here.


class NonprofitAccounting(LoginRequiredMixin, View):

    template_name = "postcards/non_profit_accounting.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get_non_profit(self):
        slug = self.kwargs["slug"]
        try:
            non_profit = NonProfit.objects.get(slug=slug)
            return non_profit
        except Exception as e:
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        profile = self.get_profile()
        non_profit = self.get_non_profit()

        allow_access = False

        ocad_profiles = [
            "president.msa.ocad@gmail.com",
            "vicepresident.msa.ocad@gmail.com",
            "zaeem.maqsood@gmail.com",
        ]
        if non_profit.slug == "ocad-msa" and profile.email in ocad_profiles:
            allow_access = True

        if profile.email == "zaeem.maqsood@gmail.com":
            allow_access = True

        if not allow_access:
            raise Http404

        # line_orders = LineOrder.objects.filter(
        #     postcard__non_profit=non_profit, created_at__gte="2021-01-01"
        # ).order_by("-created_at")

        line_orders = LineOrder.objects.filter(
            postcard__non_profit=non_profit
        ).order_by("-created_at")

        total_payout = line_orders.aggregate(Sum("amount"))["amount__sum"]
        print(total_payout)

        context["total_payout"] = total_payout
        context["non_profit"] = non_profit
        context["line_orders"] = line_orders
        context["profile"] = profile
        return render(request, self.template_name, context)


class PostCardManageOrdersView(View, SuperUserRequiredMixin):

    template_name = "postcards/manage.html"

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        get_data = self.request.GET

        if "show_all" in get_data:
            postcard_orders = LineOrder.objects.all()
        else:
            postcard_orders = LineOrder.objects.filter(
                sent_to_recipient=False
            ).order_by("created_at")

        context["orders"] = postcard_orders
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        json_list = []

        if "sent" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "sent":
                    postcard_order = LineOrder.objects.get(id=field)
                    postcard_order.sent_to_recipient = True
                    postcard_order.envelope_printed = True
                    postcard_order.front_printed = True
                    postcard_order.message_printed = True
                    postcard_order.name_printed = True
                    postcard_order.save()
                    self.send_confirmation_email(postcard_order)

        if "no_sent" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_sent":
                    postcard_order = LineOrder.objects.get(id=field)
                    postcard_order.sent_to_recipient = False
                    postcard_order.save()

        if "envelope" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "envelope":
                    print(field)
                    postcard_order = LineOrder.objects.get(id=field)
                    print(postcard_order)

                    if postcard_order.anonymous:
                        json_data["sender_name"] = ""
                        json_data["sender_line_1"] = ""
                        json_data["sender_line_2"] = ""

                    else:
                        json_data["sender_name"] = postcard_order.order.name
                        line_1 = f"{postcard_order.sender_address.street_number} {postcard_order.sender_address.route}"
                        json_data["sender_line_1"] = line_1
                        postal_code = postcard_order.sender_address.postal_code.replace(
                            " ", ""
                        )
                        cleaned_postal_code = postal_code[:3] + " " + postal_code[3:]
                        line_2 = f"{postcard_order.sender_address.locality}, {postcard_order.sender_address.administrative_area_level_1}  {cleaned_postal_code}"
                        json_data["sender_line_2"] = line_2

                    json_data["recipient_name"] = postcard_order.recipient.name
                    line_1 = f"{postcard_order.recipient.street_number} {postcard_order.recipient.route}"
                    json_data["recipient_line_1"] = line_1
                    postal_code = postcard_order.recipient.postal_code.replace(" ", "")
                    cleaned_postal_code = postal_code[:3] + " " + postal_code[3:]
                    line_2 = f"{postcard_order.recipient.locality}, {postcard_order.recipient.administrative_area_level_1}  {cleaned_postal_code}"
                    json_data["recipient_line_2"] = line_2

                    json_list.append(json_data)

        if "ap_envelope" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_envelope":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["sender_name"] = "Arqam House"
                    json_data["sender_line_1"] = ""
                    json_data["sender_line_2"] = ""
                    json_data["recipient_name"] = postcard_order.sender_address.name
                    line_1 = f"{postcard_order.sender_address.street_number} {postcard_order.sender_address.route}"
                    json_data["recipient_line_1"] = line_1
                    postal_code = postcard_order.sender_address.postal_code.replace(
                        " ", ""
                    )
                    cleaned_postal_code = postal_code[:3] + " " + postal_code[3:]
                    line_2 = f"{postcard_order.sender_address.locality}, {postcard_order.sender_address.administrative_area_level_1}  {cleaned_postal_code}"
                    json_data["recipient_line_2"] = line_2

                    json_list.append(json_data)

        if "no_envelope" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_envelope":
                    postcard_order = LineOrder.objects.get(id=field)
                    postcard_order.envelope_printed = False
                    postcard_order.save()

        if "front" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "front":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["id"] = postcard_order.postcard.id
                    json_list.append(json_data)

                    postcard_order.envelope_printed = True
                    postcard_order.save()

        if "ap_front" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_front":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["id"] = 6
                    json_list.append(json_data)

        if "no_front" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_front":
                    postcard_order = LineOrder.objects.get(id=field)
                    postcard_order.front_printed = False
                    postcard_order.save()

        if "message" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "message":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["id"] = postcard_order.postcard.id
                    json_data["message"] = "\n".join(
                        [
                            "\r".join(
                                textwrap.wrap(
                                    line,
                                    60,
                                    break_long_words=False,
                                    replace_whitespace=False,
                                )
                            )
                            for line in postcard_order.message_to_recipient.splitlines()
                            if line.strip() != ""
                        ]
                    )
                    json_list.append(json_data)

                    postcard_order.envelope_printed = True
                    postcard_order.front_printed = True
                    postcard_order.save()

        if "ap_message" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_message":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["id"] = 6
                    json_data[
                        "message"
                    ] = f"Hi {postcard_order.sender_address.name}! We wanted to give a big thank you\rfor supporting us. We hope you enjoyed using our postcard service\rand we were able to help make your loved one feel special.\rThere is nothing like receiving personal messages\rthrough the mail! You can check our new collection\rof postcards for Fall 2020 on our site!\r\rLove, Arqam house team"
                    json_list.append(json_data)

        if "no_message" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_message":
                    postcard_order = LineOrder.objects.get(id=field)
                    postcard_order.message_printed = False
                    postcard_order.save()

        if "name" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "name":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["id"] = postcard_order.postcard.id
                    json_data["name"] = postcard_order.recipient.name
                    json_list.append(json_data)

                    postcard_order.envelope_printed = True
                    postcard_order.front_printed = True
                    postcard_order.message_printed = True
                    postcard_order.save()

        if "ap_name" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "ap_name":
                    postcard_order = LineOrder.objects.get(id=field)
                    json_data["id"] = 6
                    json_data["name"] = postcard_order.sender_address.name
                    json_list.append(json_data)

        if "no_name" in data:

            for field in data:
                json_data = {}

                if field != "csrfmiddlewaretoken" and field != "no_name":
                    postcard_order = LineOrder.objects.get(id=field)
                    postcard_order.name_printed = False
                    postcard_order.save()

        if json_data:
            return JsonResponse(json_list, safe=False)

        return render(request, self.template_name, self.get_context_data())

    def send_confirmation_email(self, postcard_order):
        # Compose Email

        context = {}

        if postcard_order.finished_image:
            s3_client = boto3.client(
                "s3",
                "ca-central-1",
                config=Config(signature_version="s3v4"),
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": postcard_order.finished_image_path,
                },
                ExpiresIn=360000,
            )

            context["image_url"] = response

        subject = f"Your postcard is on it's way."
        context["postcard_order"] = postcard_order

        html_content = render_to_string(
            "emails/postcard_shipped_confirmation.html", context
        )

        text_content = strip_tags(html_content)
        from_email = f"Arqam House <info@arqamhouse.com>"
        to = [postcard_order.order.email]
        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=from_email, to=to
        )
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
        if "success" in get_data:
            context["show_confetti"] = True
            context["postcard_order"] = LineOrder.objects.all().reverse().first()

        context["postcards"] = postcards
        return context


class NonProfitPostCardListView(View):
    template_name = "postcards/non_profit_list.html"

    def get_non_profit(self):
        slug = self.kwargs["slug"]
        try:
            non_profit = NonProfit.objects.get(slug=slug)
            return non_profit
        except Exception as e:
            raise Http404

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}

        non_profit = self.get_non_profit()
        postcards = PostCard.objects.filter(hidden=False, non_profit=non_profit)

        get_data = self.request.GET
        if "success" in get_data:
            context["show_confetti"] = True
            context["postcard_order"] = LineOrder.objects.all().reverse().first()

        context["postcards"] = postcards
        context["non_profit"] = non_profit
        return context


class PostCardListView(View):
    template_name = "postcards/list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        postcards = PostCard.objects.filter(hidden=False)

        non_profit = NonProfit.objects.filter(featured=True).first()
        non_profit_postcards = PostCard.objects.filter(non_profit=non_profit)[:4]

        get_data = self.request.GET
        if "success" in get_data:
            context["show_confetti"] = True
            context["postcard_order"] = Order.objects.latest("id")

        context["postcards"] = postcards
        context["non_profit"] = non_profit
        context["non_profit_postcards"] = non_profit_postcards
        return context


def profile_exists(request):
    json_data = json.loads(request.body)
    if json_data:
        print(json_data)
        email = json_data["email"]
        try:
            profile = Profile.objects.get(email=email)
            if profile.temp_password:
                return JsonResponse({"exists": False})
            else:
                return JsonResponse({"exists": True})
        except Exception as e:
            print(e)
            return JsonResponse({"exists": False})


def stripePayment(request):
    json_data = json.loads(request.body)
    if json_data:
        print(json_data)
        postcard_id = json_data["postcard"]
        quantity = int(json_data["quantity"])
        code = json_data["promo_code"]
        donation = decimal.Decimal(json_data["donation"])
        name = json_data["name"]
        email = json_data["email"]
        add_gift_card = json_data["add_gift_card"]
        gift_card_amount = decimal.Decimal(json_data["gift_card_amount"])

        postcard = PostCard.objects.get(id=postcard_id)
        print(postcard)

        reduction = 0
        code_used = False
        if code:
            try:
                promo_code = PromoCode.objects.get(code=code.lower().strip())
                reduction = promo_code.fixed_amount
                code_used = True
            except Exception as e:
                print(e)
                reduction = 0
                return JsonResponse({"retry": True})

        if reduction != 0:
            total = int(((postcard.amount - reduction) * quantity) * 100)
            total_decimal = (postcard.amount - reduction) * quantity
        else:
            total = int((postcard.amount * quantity) * 100)
            total_decimal = postcard.amount * quantity

        # Handle Donations
        if donation:
            total = total + int(donation * 100)
            total_decimal = total_decimal + donation
            print(f" The donation is {donation}")
        else:
            print("no donation")

        # Check for gift cards
        if add_gift_card:
            total = total + int((gift_card_amount * quantity) * 100)
            total_decimal = total_decimal + (gift_card_amount * quantity)
        else:
            print("No Gift cards")

        print(total)

        if total <= 0:
            no_payment = True

            return JsonResponse(
                {
                    "retry": False,
                    "total": total,
                    "postcard_name": postcard.name,
                    "total_decimal": total_decimal,
                    "code_used": code_used,
                    "no_payment": no_payment,
                }
            )

        else:
            no_payment = False
            stripe.api_key = settings.STRIPE_SECRET_KEY

            postcard_intent = stripe.PaymentIntent.create(
                amount=total,
                currency="cad",
                description="Postcard Arqam House",
                metadata={
                    "postcard": postcard.name,
                    "postcard_amount": postcard.amount,
                    "name": name,
                    "email": email,
                },
                statement_descriptor="Postcard Arqam House",
            )

            intent_id = postcard_intent.id
            client_secret = postcard_intent.client_secret
            public_key = settings.STRIPE_PUBLIC_KEY

        return JsonResponse(
            {
                "retry": False,
                "total": total,
                "intent_id": intent_id,
                "client_secret": client_secret,
                "public_key": public_key,
                "postcard_name": postcard.name,
                "total_decimal": total_decimal,
                "code_used": code_used,
                "no_payment": no_payment,
            }
        )


class PostCardViewAllRecipients(LoginRequiredMixin, View):

    template_name = "postcards/order_view_all_recipients.html"

    def get_profile(self):

        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get_postcard(self):
        slug = self.kwargs["slug"]
        try:
            postcard = PostCard.objects.get(slug=slug)
            return postcard
        except Exception as e:
            raise Http404

    def get(self, request, *args, **kwargs):
        data = request.GET
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        data = self.request.GET
        postcard = self.get_postcard()
        profile = self.get_profile()
        recipients = Recipient.objects.filter(profile=profile)

        context["recipients"] = recipients
        context["postcard"] = postcard
        return context


class PostcardSenderAddressList(LoginRequiredMixin, View):

    template_name = "postcards/sender_address_list.html"

    def get_profile(self):
        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get_postcard(self):
        slug = self.kwargs["slug"]
        try:
            postcard = PostCard.objects.get(slug=slug)
            return postcard
        except Exception as e:
            raise Http404

    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        profile = self.get_profile()

        postcard = self.get_postcard()
        context["postcard"] = postcard
        addresses = Address.objects.filter(profile=profile).order_by("-default")

        if "recep" in data:
            context["recep"] = data["recep"]
        context["addresses"] = addresses

        context["profile"] = profile
        return render(request, self.template_name, context)


class PostCardOrderView(FormView):
    model = PostCard
    template_name = "postcards/order.html"

    def get(self, request, *args, **kwargs):

        data = request.GET

        if "quantity" in data:
            quantity = data["quantity"]

        else:
            quantity = 1

        initial_data = {}
        postcard = self.get_postcard()
        profile = self.get_profile()
        authenticated = request.user.is_authenticated
        form = PostcardOrderForm(quantity, postcard, profile, authenticated)
        return render(request, self.template_name, self.get_context_data(form=form))

    def get_success_url(self):

        postcard = self.get_postcard()

        try:
            last_order = Order.objects.all().latest("id")
            view_name = "profiles:orders:public_detail"
            return reverse(view_name, kwargs={"public_id": last_order.public_id})
        except Exception as e:
            print(e)
            view_name = "postcards:list"
            return reverse(view_name) + "?success=true"

    def get_postcard(self):
        slug = self.kwargs["slug"]
        try:
            postcard = PostCard.objects.get(slug=slug)
            return postcard
        except Exception as e:
            raise Http404

    def get_profile(self):

        try:
            profile = Profile.objects.get(email=str(self.request.user))
            return profile
        except:
            return None

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        request = self.request

        data = request.GET
        if "quantity" in data:
            quantity = int(data["quantity"])
            one = False
        else:
            quantity = 1
            one = True

        postcard = self.get_postcard()

        try:
            last_postcard = LineOrder.objects.filter(postcard=postcard).latest("id")
            context["last_postcard"] = last_postcard
        except Exception as e:
            print(e)

        profile = self.get_profile()
        if profile:
            context["profile"] = profile

            # default sender
            try:
                default_address = Address.objects.filter(
                    profile=profile, default=True
                ).first()
                context["default_address"] = default_address
            except Exception as e:
                print(e)
                context["default_address"] = False

            # If new sender
            if "sender" in data:
                try:
                    chosen_sender = Address.objects.get(
                        profile=profile, id=data["sender"]
                    )
                    context["chosen_sender"] = chosen_sender
                except Exception as e:
                    print(e)

            # All recipients
            recipients = Recipient.objects.filter(profile=profile).order_by(
                "-created_at"
            )
            context["recipients"] = recipients

        context["quantity_str"] = quantity
        postcard_amount = 5 * quantity
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

        if "quantity" in data:
            quantity = int(data["quantity"])
        else:
            quantity = 1

        profile = self.get_profile()
        postcard = self.get_postcard()
        authenticated = request.user.is_authenticated
        form = PostcardOrderForm(
            data=data,
            quantity=quantity,
            postcard=postcard,
            profile=profile,
            authenticated=authenticated,
        )

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)

    def form_valid(self, form, request):

        # Post data
        data = request.POST

        # Get Data
        get_data = request.GET

        anonymous = form.cleaned_data.get("anonymous")

        # Get the quantity
        # There will always be a quantity value coming from quantity_str
        quantity = int(data["quantity"])

        # grab postcard object
        postcard = self.get_postcard()

        # Set line amount and order amounts
        line_amount = postcard.amount
        amount = postcard.amount * quantity

        # --------------------------- Handle Promo Codes --------------------------
        code = form.cleaned_data.get("promo_code")

        # Read the promo code if it exists
        try:
            promo_code = PromoCode.objects.get(code=code.lower())
            # Set the line amount based off of the promo code reduction
            line_amount = postcard.amount - promo_code.fixed_amount
            # set the amount based on the promo code reduction
            amount = (postcard.amount - promo_code.fixed_amount) * quantity

        # If code does not exist
        except Exception as e:
            promo_code = None

        # --------------------------- Handle Promo Codes --------------------------

        # --------------------------- Handle donations --------------------------
        donation = 0
        line_donation = 0
        total_donation = 0

        # Check if the postcard is even a non-profit card or not
        if postcard.non_profit:

            donation = form.cleaned_data.get("donation")
            if donation:
                donation = decimal.Decimal(donation)
            else:
                donation = 0

            # set the line donation
            line_donation = postcard.non_profit.amount

            if donation > 0:
                amount = amount + donation

            total_donation = donation + (line_donation * quantity)

        # --------------------------- Handle donations --------------------------

        # --------------------------- Handle Gift Cards --------------------------
        gift_card_amount = 0
        gift_card = None
        add_gift_card = form.cleaned_data.get("add_gift_card")
        if add_gift_card:
            gift_card = data["giftCards"]
            gift_card_amount = form.cleaned_data.get("gift_card_amount")
            gift_card_amount = decimal.Decimal(gift_card_amount)

            if gift_card_amount > 0:
                gift_card_amount_total = gift_card_amount * quantity
                line_amount = amount + gift_card_amount
                amount = amount + gift_card_amount_total

        # --------------------------- Handle Gift Cards --------------------------

        stripe.api_key = settings.STRIPE_SECRET_KEY

        # 1. User logged in
        # 2. User logged in but uses different sender information
        # 3. User not logged in but their profile exists
        # 4. User not logged in, we need to create their profile

        accept_form_data = True

        # Determine if the user is logged in or not
        if request.user.is_authenticated:

            email = request.user.email
            # Grab the users profile if logged in
            profile = Profile.objects.get(email=email)

            # Determine if user is using default information or ad
            if "sender" in get_data:
                sender_address = Address.objects.get(
                    profile=profile, id=get_data["sender"]
                )
                accept_form_data = False

            else:

                # We have to add a try block here because some users might exist
                # Without an address
                try:
                    sender_address = Address.objects.filter(
                        profile=profile, default=True
                    ).first()
                    accept_form_data = False

                # If the sender address does not exist we are expecting data from the form
                except Exception as e:
                    print(e)
                    accept_form_data = True

            # Use sender address as variables if we don't need the form data
            if not accept_form_data:
                name = sender_address.name
                apt_number = sender_address.apt_number
                street_number = sender_address.street_number
                route = sender_address.route
                locality = sender_address.locality
                administrative_area_level_1 = sender_address.administrative_area_level_1
                address = sender_address.address
                postal_code = sender_address.postal_code

        # If we need to accept the form data
        if accept_form_data:
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email").lower()
            apt_number = form.cleaned_data.get("apt_number")
            street_number = form.cleaned_data.get("street_number")
            route = form.cleaned_data.get("route")
            locality = form.cleaned_data.get("locality")
            administrative_area_level_1 = form.cleaned_data.get(
                "administrative_area_level_1"
            )
            address = form.cleaned_data.get("address")
            postal_code = form.cleaned_data.get("postal_code")

            password_entered = False
            if form.cleaned_data.get("password") != "":
                print("There is a password")
                password = form.cleaned_data.get("password")
                password_entered = True

        # If the user is not authenticatted
        if not request.user.is_authenticated:

            # We need to check if the user exists or not
            try:
                profile = Profile.objects.get(email=email)

                # Check to see if an existing user entered a password to make an account
                # If so update the password and log them in
                if password_entered:
                    profile.set_password(password)
                    profile.save()

                    # Login the user
                    login(request, profile)

            except Exception as e:
                print(e)

                # Check if there is a password set by the user
                if password_entered:
                    profile = Profile.objects.create_user(
                        name=name, email=email, password=password
                    )

                    # Login the user
                    login(request, profile)

                else:
                    profile_temp_password = get_random_string(length=10)
                    profile = Profile.objects.create_user(
                        name=name,
                        email=email,
                        password=profile_temp_password,
                        temp_password=profile_temp_password,
                    )

        # create the sender address if we need to collect data
        # and once we have a profile object
        if accept_form_data:
            sender_address = Address.objects.create(
                profile=profile,
                name=name,
                address=address,
                default=True,
                apt_number=apt_number,
                street_number=street_number,
                route=route,
                locality=locality,
                administrative_area_level_1=administrative_area_level_1,
                postal_code=postal_code,
            )

        if amount <= 0:
            print(f"For some reason the amount is {amount}")
        else:
            try:
                stripe_token = data["intent_id"]
            except Exception as e:
                print(f"For some reason the amount is {amount}")
                print(e)
                print("Exception 2")
                form.add_error(
                    None,
                    "Your payment was not processed. A network error prevented payment processing, please try again later.",
                )
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
            print("Exception 3")
            form.add_error(
                None,
                "Your payment was not processed. A network error prevented payment processing, please try again later.",
            )
            return self.render_to_response(self.get_context_data(form=form))

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
            print("Exception 1")

        # -------------------------

        postcard_orders = []

        order = Order.objects.create(
            profile=profile,
            name=name,
            email=email,
            amount=amount,
            donation_amount=donation,
            fulfilled=False,
            total_donation_amount=total_donation,
        )
        for x in range(quantity):

            if not accept_form_data:

                recipient = form.cleaned_data.get(f"recipient_{x}")
                recipient.counter += 1
                recipient.save()

            else:

                recipient_name = form.cleaned_data.get(f"{x}_recipient_name")
                recipient_address = form.cleaned_data.get(f"autocomplete{x}")
                recipient_apt_number = form.cleaned_data.get(f"apt_number_{x}")
                recipient_street_number = form.cleaned_data.get(f"street_number_{x}")
                recipient_route = form.cleaned_data.get(f"route_{x}")
                recipient_locality = form.cleaned_data.get(f"locality_{x}")
                recipient_administrative_area_level_1 = form.cleaned_data.get(
                    f"administrative_area_level_1_{x}"
                )
                recipient_postal_code = form.cleaned_data.get(f"postal_code_{x}")

                recipient, created = Recipient.objects.get_or_create(
                    profile=profile,
                    name=recipient_name,
                    email=None,
                    address=recipient_address,
                    apt_number=recipient_apt_number,
                    street_number=recipient_street_number,
                    route=recipient_route,
                    locality=recipient_locality,
                    administrative_area_level_1=recipient_administrative_area_level_1,
                    postal_code=recipient_postal_code,
                    counter=1,
                )

                if not created:
                    recipient.counter += 1
                    recipient.save()

            message_to_recipient = form.cleaned_data.get(f"{x}_message_to_recipient")

            line_order = LineOrder.objects.create(
                order=order,
                recipient=recipient,
                promo_code=promo_code,
                postcard=postcard,
                sender_address=sender_address,
                message_to_recipient=message_to_recipient,
                amount=line_amount,
                donation_amount=donation,
                anonymous=anonymous,
                add_gift_card=add_gift_card,
                gift_card=gift_card,
                gift_card_amount=gift_card_amount,
            )

            if amount <= 0:
                pass
            else:
                charge = stripe.PaymentIntent.retrieve(stripe_token)
                order.payment_intent_id = charge["id"]
                order.payment_method_id = charge["payment_method"]
                order.save()

            postcard_orders.append(line_order)

        if promo_code != None:
            promo_code.used += quantity
            promo_code.save()

        if settings.DEBUG == False and order.email != "info@arqamhouse.com":
            try:
                self.send_text_message(order, postcard_orders, postcard)
            except Exception as e:
                print(e)

            try:
                self.send_confirmation_email(order, postcard_orders, postcard)
            except Exception as e:
                print(e)

        postcard.amount_sold += 1
        postcard.save()

        messages.success(request, "Order Placed!")
        valid_data = super(PostCardOrderView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form, request):
        print(form.errors)

        return self.render_to_response(self.get_context_data(form=form))

    def send_text_message(self, order, postcard_orders, postcard):
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)

        postcard_amounts = len(postcard_orders)
        sender_name = order.name

        if postcard_amounts > 1:
            message = client.messages.create(
                body=f"You have {postcard_amounts} new postcard orders made by {sender_name}",
                from_="+16475571902",
                to="+16472985582",
            )
        else:
            postcard_order = order
            message = client.messages.create(
                body="You have a new postcard order by %s, they want to send it to %s."
                % (postcard_order.name, postcard_orders[0].recipient.name),
                from_="+16475571902",
                to="+16472985582",
            )

    def send_confirmation_email(self, order, postcard_orders, postcard):
        # Compose Email

        context = {}

        postcard_amounts = len(postcard_orders)
        context["order"] = order
        context["postcard"] = postcard
        # s3_client = boto3.client('s3', 'ca-central-1', config=Config(signature_version='s3v4'),
        #                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        # response = s3_client.generate_presigned_url('get_object', Params={
        #     'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': postcard_order.post_card.image_1_path}, ExpiresIn=360000)

        subject = f"Thank you for your purchase, {order.name}."

        # context["image_url"] = response

        if order.donation_amount > 0:
            context["donated"] = True
        else:
            context["donated"] = False

        if postcard_amounts == 1:
            context["recipient"] = postcard_orders[0].recipient
            context["line_order"] = postcard_orders[0]
            html_content = render_to_string(
                "emails/postcard_confirmation.html", context
            )

        else:
            context["postcard_amounts"] = postcard_amounts
            context["postcard_orders"] = postcard_orders
            html_content = render_to_string(
                "emails/postcard_confirmation_multiple.html", context
            )

        text_content = strip_tags(html_content)
        from_email = f"Arqam House <info@arqamhouse.com>"
        to = [order.email]
        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=from_email, to=to
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return "Done"
