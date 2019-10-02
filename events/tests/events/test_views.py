import decimal

from django.test import TestCase
from houses.models import House, HouseUser
from events.models import Event, EventEmailConfirmation, EventQuestion, Ticket
from profiles.models import Profile

from django.urls import reverse


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

        # Test Questions - There shouldnt be any
        events = Event.objects.inactive_events()
        self.assertQuerysetEqual(response.context['events'], events)
    







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

        
