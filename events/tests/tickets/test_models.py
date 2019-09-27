
from django.test import TestCase
from events.models import Ticket
from houses.models import House
from events.models import Event
from django.urls import reverse


class TicketModelTestCase(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")
        event = Event.objects.create(house=house, title="Arqam House Test Event", url="test-1", active=False)
        ticket1 = Ticket.objects.create(event=event, title="Ticket", free=True)
        ticket2 = Ticket.objects.create(event=event, title="Ticket", paid=True, price=5.00, pass_fee=True)
        ticket3 = Ticket.objects.create(event=event, title="Ticket", paid=True, price=5.00, pass_fee=False)

    def test_ticket_title(self):
        ticket = Ticket.objects.get(id=1)
        self.assertEquals(ticket.__str__(), 'Ticket')

    def test_ticket_slugs_are_unique(self):
        ticket1 = Ticket.objects.get(id=1)
        ticket2 = Ticket.objects.get(id=2)
        self.assertNotEquals(ticket1.slug, ticket2.slug)

    def test_update_ticket_view(self):
        ticket1 = Ticket.objects.get(id=1)
        view = ticket1.update_ticket_view()
        self.assertEquals(view, '/events/test-1/tickets/update/ticket')

    def test_percentage_color(self):
        ticket1 = Ticket.objects.get(id=1)
        ticket1.amount_available = 10
        ticket1.amount_sold = 1
        ticket1.save()
        # Test Green Color
        self.assertEquals(ticket1.percentage_color(), 'bg-success')

        ticket1.amount_sold = 6
        ticket1.save()
        # Test Blue Color
        self.assertEquals(ticket1.percentage_color(), '')

        ticket1.amount_sold = 10
        ticket1.save()
        # Test Blue Color
        self.assertEquals(ticket1.percentage_color(), 'bg-danger')

    def test_ticket_pricing(self):
        ticket2 = Ticket.objects.get(id=2)
        ticket3 = Ticket.objects.get(id=3)

        self.assertEquals(ticket2.buyer_price, 5.50)
        self.assertEquals(ticket3.buyer_price, 5.00)
        self.assertEquals(ticket2.fee, 0.50)
        


