import decimal
import stripe

from django.conf import settings
from django.test import TestCase
from houses.models import House, HouseUser
from payments.models import HouseBalance, HouseBalanceLog
from events.models import (Event, EventEmailConfirmation, EventQuestion, Ticket, EventCart, EventCartItem, AttendeeCommonQuestions, Attendee)
from profiles.models import Profile
from questions.models import Question, MultipleChoice
from cities_light.models import City, Region, Country

from django.urls import reverse


class EventCheckoutViewTest(TestCase):

    def setUp(self):

        country = Country.objects.create(name="Canada", continent="North America")
        region = Region.objects.create(country=country, name="Ontario")
        city = City.objects.create(country=country, region=region, name="Ajax")
        house = House.objects.create(name="Arqam House")
        house_balance = HouseBalance.objects.create(house=house, balance=0.00)
        house_balance_logs = HouseBalanceLog.objects.create(house_balance=house_balance, balance=0.00, opening_balance=True)
        profile = Profile.objects.create_user(email='zaeem.maqsood@gmail.com', password="Ed81ae9600!", is_active=True)
        profile.house = house
        profile.save()
        house_user = HouseUser.objects.create(profile=profile, house=house, role='admin')
        # Create active event
        event = Event.objects.create(house=house, title="Arqam House Test Event", url="test-1", active=True)
        attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
        attendee_common_questions.age = True
        attendee_common_questions.gender = True
        attendee_common_questions.address = True
        attendee_common_questions.save()

        ticket = Ticket.objects.create(event=event, title="Paid Ticket", paid=True, price=5.00, pass_fee=True)
        ticket2 = Ticket.objects.create(event=event, title="Free Ticket", free=True)
        ticket3 = Ticket.objects.create(event=event, title="Donation Ticket", donation=True)

        question = Question.objects.create(house=house, title="Simple Question", required=True, question_type="Simple", approved=True)
        event_question = EventQuestion.objects.create(event=event, question=question, order_question=True)
        event_question.tickets.set(Ticket.objects.filter(event=event))

        question2 = Question.objects.create(house=house, title="Long Question", required=True, question_type="Long", approved=True)
        event_question2 = EventQuestion.objects.create(event=event, question=question2, order_question=True)
        event_question2.tickets.set(Ticket.objects.filter(event=event))

        question3 = Question.objects.create(house=house, title="Multiple Choice Question", required=True, question_type="Multiple Choice", approved=True)
        option_a = MultipleChoice.objects.create(question=question, title="Order Question")
        option_b = MultipleChoice.objects.create(question=question, title="Something Else")
        option_c = MultipleChoice.objects.create(question=question, title="Another Thing")
        event_question3 = EventQuestion.objects.create(event=event, question=question3, order_question=True)
        event_question3.tickets.set(Ticket.objects.filter(event=event))


        cart = EventCart.objects.create(event=event, pay=True)
        cart_item = EventCartItem.objects.create(event_cart=cart, ticket=ticket, quantity=2)
        cart_item2 = EventCartItem.objects.create(event_cart=cart, ticket=ticket2, quantity=2)
        cart_item3 = EventCartItem.objects.create(event_cart=cart, ticket=ticket3, quantity=2, donation_amount=10.00)

    def test_context_data_on_get_call(self):
        event = Event.objects.get(slug="test-1")
        attendee_common_questions = AttendeeCommonQuestions.objects.get(
            event=event)
        cart = EventCart.objects.get(event=event)
        cart_items = EventCartItem.objects.filter(event_cart=cart)
        public_key = settings.STRIPE_PUBLIC_KEY
        total = cart.total * decimal.Decimal(100.00)

        session = self.client.session
        session['cart'] = cart.id
        session.save()

        response = self.client.get(
            reverse("events:checkout", kwargs={'slug': event.slug}))
        self.assertEqual(response.status_code, 200)
        # Test Cart Items
        self.assertQuerysetEqual(
            list(response.context['cart_items']), cart_items, transform=lambda x: x)
        # Test Cart
        self.assertEqual(response.context['cart'], cart)
        # Test Attendee Commone Questions
        self.assertEqual(
            response.context['attendee_common_questions'], attendee_common_questions)
        # Test Event
        self.assertEqual(response.context['event'], event)
        # Test public_key
        self.assertEqual(response.context['public_key'], public_key)
        # Test Total
        self.assertEqual(response.context['total'], total)
        # Test Data
        self.assertEqual(response.context['data'], None)

    def test_post_call(self):

        # Get all the things I need to make the post reques
        event = Event.objects.get(slug="test-1")
        event_questions = EventQuestion.objects.filter(event=event)
        cart = EventCart.objects.get(event=event)
        cart_items = EventCartItem.objects.filter(event_cart=cart)

        # Set the sessions
        session = self.client.session
        session['cart'] = cart.id
        session.save()

        # Start making the post data
        data = {}
        data["name"] = "Zaeem Maqsood"
        data["email"] = "zaeem.maqsood@gmail.com"

        # set the order questions
        for event_question in event_questions:
            data["%s_order_question" % (event_question.question.id)] = "Order Question"

        # Set ticket questions
        for cart_item in cart_items:
            for quantity in range(cart_item.quantity):

                # Set name
                data["%s_%s_name" % (quantity, cart_item.ticket.id)] = "Zaeem Maqsood"
                # Set age
                data["%s_%s_age" % (quantity, cart_item.ticket.id)] = 24
                # Set Gender
                data["%s_%s_gender" % (quantity, cart_item.ticket.id)] = "male"
                # Set Address
                data["%s_%s_address" % (quantity, cart_item.ticket.id)] = "47 Denny Street, Ajax, ON, Canada"

                for event_question in event_questions:
                    data["%s_%s_%s" % (quantity, event_question.question.id, cart_item.ticket.id)] = "Ticket Question"

        public_key = settings.STRIPE_PUBLIC_KEY
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = stripe.Token.create(
            card={
                "number": '4242424242424242',
                "exp_month": 12,
                "exp_year": 2020,
                "cvc": '123'
            },
        )
        data["stripeToken"] = token.id

        # Get the post response 
        response = self.client.post(reverse("events:checkout", kwargs={'slug': event.slug}), data, follow=True)
        # Check if we are all good
        self.assertEqual(response.status_code, 200)

        # Check all cart variables
        cart = EventCart.objects.get(event=event, processed=True)
        self.assertEqual(cart.processed, True)
        self.assertEqual(cart.total_no_fee, round(decimal.Decimal(30.00),2))
        self.assertEqual(cart.total, round(decimal.Decimal(32.40),2))
        self.assertEqual(cart.total_fee, round(decimal.Decimal(2.40), 2))
        self.assertEqual(cart.arqam_charge, round(decimal.Decimal(1.16), 2))
        self.assertEqual(cart.stripe_charge, round(decimal.Decimal(1.24), 2))

        # Check all ticket
        tickets = Ticket.objects.filter(event=event)
        for ticket in tickets:
            self.assertEqual(ticket.amount_sold, 2)
            self.assertEqual(ticket.amount_available, 500)

        # Check all attendees
        attendees = Attendee.objects.filter(order__event=event)
        for attendee in attendees:
            if attendee.ticket.title == "Donation Ticket":
                self.assertEqual(attendee.ticket_price, round(decimal.Decimal(10.00),2))
                self.assertEqual(attendee.ticket_buyer_price, round(decimal.Decimal(10.70),2))
                self.assertEqual(attendee.ticket_fee, round(decimal.Decimal(0.70),2))
                self.assertEqual(attendee.ticket_pass_fee, True)
            elif attendee.ticket.title == "Paid Ticket":
                self.assertEqual(attendee.ticket_price, round(decimal.Decimal(5.00),2))
                self.assertEqual(attendee.ticket_buyer_price, round(decimal.Decimal(5.50),2))
                self.assertEqual(attendee.ticket_fee, round(decimal.Decimal(0.50),2))
                self.assertEqual(attendee.ticket_pass_fee, True)
            else:
                self.assertEqual(attendee.ticket_price, round(decimal.Decimal(0.00),2))
                self.assertEqual(attendee.ticket_buyer_price, round(decimal.Decimal(0.00),2))
                self.assertEqual(attendee.ticket_fee, round(decimal.Decimal(0.00),2))
                
            self.assertEqual(attendee.name, "Zaeem Maqsood")
            self.assertEqual(attendee.age, 24)
            self.assertEquals(attendee.address, "47 Denny Street, Ajax, ON, Canada") 








        
        





class PastEventsViewTest(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")
        profile = Profile.objects.create_user(email='zaeem.maqsood@gmail.com', password="Ed81ae9600!", is_active=True)
        profile.house = house
        profile.save()
        house_user = HouseUser.objects.create(profile=profile, house=house, role='admin')
        # Create active event
        event = Event.objects.create(house=house, title="Arqam House Test Event", url="test-1", active=True)
        # Create inactive event
        event = Event.objects.create(house=house, title="Arqam House Test Event", url="test-2", active=False)
        # Create Deleted Event
        event = Event.objects.create(house=house, title="Arqam House Test Event", url="test-3", active=True, deleted=True)

        self.client.login(email='zaeem.maqsood@gmail.com', password='Ed81ae9600!')

    def test_one_past_event_and_one_deleted_event(self):
        
        event = Event.objects.get(slug="test-1")
        response = self.client.get(reverse("events:past"))
        # Test the response
        self.assertEqual(response.status_code, 200)
        # Test inactive events
        events = Event.objects.inactive_events()
        self.assertQuerysetEqual(response.context['events'], events, transform=lambda x: x)
        # Test active events
        events = Event.objects.deleted_events()
        self.assertQuerysetEqual(response.context['deleted_events'], events, transform=lambda x: x)
        # Test House
        profile = response.context['user']
        house = profile.house
        self.assertEqual(house.name, "Arqam House")
        # Test Dashboard events
        dashboard_events = Event.objects.active_events().filter(house=house) 
        self.assertQuerysetEqual(response.context['dashboard_events'], dashboard_events, transform=lambda x: x)
        # Test tab
        self.assertEqual(response.context['past_event_tab'], True)


        
    







class EventDashboardViewTests(TestCase):

    def setUp(self):
        # Set up house
        house = House.objects.create(name="Arqam House")

        profile = Profile.objects.create_user(email='zaeem.maqsood@gmail.com', password="Ed81ae9600!", is_active=True)
        profile.house = house
        profile.save()
        house_user = HouseUser.objects.create(profile=profile, house=house, role='admin')
        # Create an event
        event = Event.objects.create(house=house, title="Arqam House Test Event", url="test-1", active=True)

        self.client.login(email='zaeem.maqsood@gmail.com', password='Ed81ae9600!')

    
    def test_fresh_dashboard(self):

        event = Event.objects.get(slug="test-1")
        view = event.get_event_dashboard()
        response = self.client.get(event.get_event_dashboard())

        # Test the response
        self.assertEqual(response.status_code, 200)

        # Test Email Is working
        email = EventEmailConfirmation.objects.get(event=event)
        self.assertEquals(response.context['email'], email)

        # Test Questions - There shouldnt be any
        questions = EventQuestion.objects.filter(event=event, question__deleted=False, question__approved=True)
        self.assertQuerysetEqual(response.context['questions'], [])

        # Test Tickets - shouldnt be any
        tickets = Ticket.objects.filter(event=event, deleted=False)
        self.assertQuerysetEqual(response.context['tickets'], [])

        # Test Total Sales
        total_sales = decimal.Decimal(0.00)
        self.assertEquals(response.context['total_sales'], decimal.Decimal(0.00))

        
