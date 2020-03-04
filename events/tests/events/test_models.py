# --------------------- Events Tests------------------------

from django.test import TestCase
from houses.models import House
from events.models import Event


class EventModelTestCase(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")

        # Create an event
        Event.objects.create(
            house=house, title="Arqam House Test Event", url="test-1", active=False)

        # Create another event using same title and url feilds
        Event.objects.create(
            house=house, title="Arqam House Test Event", url="test-1", active=True)

        Event.objects.create(
            house=house, title="Arqam House Test Event", active=True)

    def test_event_title(self):
        event = Event.objects.get(slug="test-1")
        self.assertEqual(event.__str__(), 'Arqam House Test Event')

    def test_event_slugs_are_unique(self):
        events = Event.objects.filter(slug="test-1")
        self.assertEqual(events.count(), 1)

    def test_active_events(self):
        events = Event.objects.active_events()
        self.assertEqual(events.count(), 2)

    def test_inactive_events(self):
        events = Event.objects.inactive_events()
        self.assertEqual(events.count(), 1)

    def test_get_email_confirmation_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.get_email_confirmation_view()
        self.assertEqual(view, '/events/test-1/emails/email-confirmation')

    def test_get_landing_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.get_landing_view()
        self.assertEqual(view, '/events/test-1/')

    def test_get_update_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.get_update_view()
        self.assertEqual(view, '/events/test-1/update')

    def test_get_event_dashboard(self):
        event = Event.objects.get(slug="test-1")
        view = event.get_event_dashboard()
        self.assertEqual(view, '/events/test-1/dashboard')

    def test_create_free_ticket(self):
        event = Event.objects.get(slug="test-1")
        view = event.create_free_ticket()
        self.assertEqual(view, '/events/test-1/tickets/create/free')

    def test_create_paid_ticket(self):
        event = Event.objects.get(slug="test-1")
        view = event.create_paid_ticket()
        self.assertEqual(view, '/events/test-1/tickets/create/paid')

    def test_create_donation_ticket(self):
        event = Event.objects.get(slug="test-1")
        view = event.create_donation_ticket()
        self.assertEqual(view, '/events/test-1/tickets/create/donation')

    def test_list_tickets_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_tickets_view()
        self.assertEqual(view, '/events/test-1/tickets/list')

    def test_list_questions_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_questions_view()
        self.assertEqual(view, '/events/test-1/questions')

    def test_list_answers_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_answers_view()
        self.assertEqual(view, '/events/test-1/answers/')

    def test_list_answers_analytic_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_answers_analytic_view()
        self.assertEqual(view, '/events/test-1/answers/analytic')

    def test_create_question(self):
        event = Event.objects.get(slug="test-1")
        view = event.create_question()
        self.assertEqual(view, '/questions/events/%s/create/' % (event.id))

    def test_list_orders_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_orders_view()
        self.assertEqual(view, '/events/test-1/orders/')

    def test_list_attendees_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_attendees_view()
        self.assertEqual(view, '/events/test-1/attendees/')

    def test_list_discounts_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.list_discounts_view()
        self.assertEqual(view, '/events/test-1/discounts')

    def test_create_discount_view(self):
        event = Event.objects.get(slug="test-1")
        view = event.create_discount_view()
        self.assertEqual(view, '/events/test-1/discounts/create')


    




