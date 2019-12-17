import decimal
from django.test import TestCase
from houses.models import House
from events.models import Event, EventCart, EventCartItem, Ticket, EventDiscount




class EventCartAndCartItemsTestCase(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")

        # Create an event
        Event.objects.create(house=house, title="Arqam House Test Event", url="test-1", active=False)

    

    def test_event_cart_discount_code_works(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=5.00, buyer_price=5.50, fee=0.50, min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(
            event=event, code="ArqamLove", fixed_amount=3.00, total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        event_cart = EventCart.objects.get(event=event)
        
        self.assertEqual(event_cart.invalid_discount_code, False)
        self.assertEqual(event_cart.discount_code, event_discount)


    def test_event_cart_discount_code_doesnt_work(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=5.00, buyer_price=5.50, fee=0.50, min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        
        event_cart.invalid_discount_code = True
        event_cart.save()

        event_cart = EventCart.objects.get(event=event)
        
        self.assertEqual(event_cart.invalid_discount_code, True)


    def test_event_cart_update_tickets_available_method(self):
            event = Event.objects.get(slug="test-1")
            event_cart = EventCart.objects.create(event=event)

            ticket = Ticket.objects.create(
                event=event, title="Paid Ticket", paid=True, price=5.00, pass_fee=True, amount_available=200)

            cart_item_1 = EventCartItem.objects.create(
                event_cart=event_cart, ticket=ticket, quantity=3, paid_ticket=True, pass_fee=True, ticket_price=5.00, ticket_buyer_price=5.50, ticket_fee=0.50,
                cart_item_total_no_fee=15.00, cart_item_total=16.50, cart_item_fee=1.50)

            event_cart.update_tickets_available()
            ticket = Ticket.objects.get(title="Paid Ticket")
            self.assertEqual(ticket.amount_sold, 3)

    
    def test_cart_item_with_paid_ticket_and_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event, pay=True)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 1", price=5.00, buyer_price=5.50, fee=0.50, min_amount=0, max_amount=10, paid=True, pass_fee=True,
            amount_available=500, refund_policy="standard")

        
        # Cart Items
        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, True)
        self.assertEqual(cart_item.ticket_price, 5.00)
        self.assertEqual(float(cart_item.ticket_buyer_price), 5.5)
        self.assertEqual(float(cart_item.ticket_fee), 0.50)
        self.assertEqual(cart_item.cart_item_total_no_fee, 5.00)
        self.assertEqual(float(cart_item.cart_item_total), 5.50)
        self.assertEqual(float(cart_item.cart_item_fee), 0.50)
        self.assertEqual(cart_item.discount_code_activated, False)



    def test_cart_item_with_paid_ticket_and_dont_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, False)
        self.assertEqual(cart_item.ticket_price, 5.00)
        self.assertEqual(float(cart_item.ticket_buyer_price), 5.0)
        self.assertEqual(float(cart_item.ticket_fee), 0.50)
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 4.50)
        self.assertEqual(float(cart_item.cart_item_total), 5.0)
        self.assertEqual(float(cart_item.cart_item_fee), 0.50)
        self.assertEqual(cart_item.discount_code_activated, False)



    def test_cart_item_with_discount_code_fixed_amount_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=True,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", fixed_amount=decimal.Decimal(3.00), total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_fixed_amount), 3.00)
        self.assertEqual(cart_item.ticket_price, 2.00)
        self.assertEqual(float(cart_item.discount_amount), 3.50)
        self.assertEqual(float(cart_item.ticket_fee), 0.38)
        self.assertEqual(cart_item.cart_item_total_no_fee, 2.00)
        self.assertEqual(float(cart_item.ticket_buyer_price), 2.38)
        self.assertEqual(float(cart_item.cart_item_total), 2.38)
        self.assertEqual(float(cart_item.cart_item_fee), 0.38)
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, True)



    def test_cart_item_with_discount_code_fixed_amount_dont_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", fixed_amount=decimal.Decimal(3.00), total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        cart_item = EventCartItem.objects.get(event_cart=event_cart, ticket=ticket)

        print("\n\nHEEELOOOOO\n\n")
        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_fixed_amount), 3.00)
        self.assertEqual(cart_item.ticket_price, 2.00)
        self.assertEqual(float(cart_item.discount_amount), 3.00)
        self.assertEqual(float(cart_item.ticket_fee), 0.38)
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 1.62)
        self.assertEqual(float(cart_item.ticket_buyer_price), 2.00)
        self.assertEqual(float(cart_item.cart_item_total), 2.00)
        self.assertEqual(float(cart_item.cart_item_fee), 0.38)
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, False)


    

    def test_cart_item_with_discount_code_percentage_amount_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=True,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", percentage_amount=50, total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_percentage_amount), 50)
        self.assertEqual(float(cart_item.ticket_price), 2.50)
        self.assertEqual(float(cart_item.discount_amount), 3.00)
        self.assertEqual("{:.1f}".format(cart_item.ticket_fee), str(0.40))
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 2.50)
        self.assertEqual(float(cart_item.ticket_buyer_price), 2.90)
        self.assertEqual(float(cart_item.cart_item_total), 2.90)
        self.assertEqual("{:.1f}".format(cart_item.cart_item_fee), str(0.40))
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, True)



    def test_cart_item_with_discount_code_percentage_amount_dont_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", percentage_amount=50, total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_percentage_amount), 50)
        self.assertEqual(float(cart_item.ticket_price), 2.50)
        self.assertEqual(float(cart_item.discount_amount), 2.50)
        self.assertEqual("{:.1f}".format(cart_item.ticket_fee), str(0.40))
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 2.10)
        self.assertEqual(float(cart_item.ticket_buyer_price), 2.50)
        self.assertEqual(float(cart_item.cart_item_total), 2.50)
        self.assertEqual("{:.1f}".format(cart_item.cart_item_fee), str(0.40))
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, False)


    

    def test_cart_item_with_discount_code_percentage_amount_dont_pass_fee(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", percentage_amount=50, total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_percentage_amount), 50)
        self.assertEqual(float(cart_item.ticket_price), 2.50)
        self.assertEqual(float(cart_item.discount_amount), 2.50)
        self.assertEqual("{:.1f}".format(cart_item.ticket_fee), str(0.40))
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 2.10)
        self.assertEqual(float(cart_item.ticket_buyer_price), 2.50)
        self.assertEqual(float(cart_item.cart_item_total), 2.50)
        self.assertEqual("{:.1f}".format(cart_item.cart_item_fee), str(0.40))
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, False)


    


    def test_cart_item_with_discount_code_fixed_amount_pass_fee_less_than_1_dollar(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=True,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", fixed_amount=decimal.Decimal(5.00), total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_fixed_amount), 5.50)
        self.assertEqual(float(cart_item.ticket_price), 0.00)
        self.assertEqual(float(cart_item.discount_amount), 5.50)
        self.assertEqual("{:.1f}".format(cart_item.ticket_fee), str(0.00))
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 0.00)
        self.assertEqual(float(cart_item.ticket_buyer_price), 0.00)
        self.assertEqual(float(cart_item.cart_item_total), 0.00)
        self.assertEqual("{:.1f}".format(cart_item.cart_item_fee), str(0.00))
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, True)



    def test_cart_item_with_discount_code_fixed_amount_dont_pass_fee_less_than_1_dollar(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
            event=event, title="Paid Mega Test 2", price=decimal.Decimal(5.00), buyer_price=decimal.Decimal(5.50), fee=decimal.Decimal(0.50), min_amount=0, max_amount=10, paid=True, pass_fee=False,
            amount_available=500, refund_policy="standard")

        event_discount = EventDiscount.objects.create(event=event, code="ArqamLove", fixed_amount=decimal.Decimal(5.00), total_uses=10)
        event_discount.tickets.add(ticket)
        event_discount.save()

        event_cart.discount_code = event_discount
        event_cart.invalid_discount_code = False
        event_cart.save()

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)

        self.assertEqual(cart_item.discount_code_activated, True)
        self.assertEqual(float(cart_item.discount_fixed_amount), 5.00)
        self.assertEqual(float(cart_item.ticket_price), 0.00)
        self.assertEqual(float(cart_item.discount_amount), 5.00)
        self.assertEqual("{:.1f}".format(cart_item.ticket_fee), str(0.00))
        self.assertEqual(float(cart_item.cart_item_total_no_fee), 0.00)
        self.assertEqual(float(cart_item.ticket_buyer_price), 0.00)
        self.assertEqual(float(cart_item.cart_item_total), 0.00)
        self.assertEqual("{:.1f}".format(cart_item.cart_item_fee), str(0.00))
        self.assertEqual(cart_item.paid_ticket, True)
        self.assertEqual(cart_item.pass_fee, False)
        
        
    

    def test_cart_item_with_free_ticket(self):
        event = Event.objects.get(slug="test-1")
        event_cart = EventCart.objects.create(event=event)

        ticket = Ticket.objects.create(
                event=event, title="Free Mega Test 1", buyer_price=0.00, min_amount=0, max_amount=10, free=True,
                amount_available=500)

        cart_item = EventCartItem.objects.create(event_cart=event_cart, ticket=ticket, quantity=1)
        self.assertEqual(cart_item.paid_ticket, False)
        self.assertEqual(cart_item.free_ticket, True)
        self.assertEqual(cart_item.ticket_price, 0.00)
        self.assertEqual(float(cart_item.ticket_buyer_price), 0.00)
        self.assertEqual(float(cart_item.ticket_fee), 0.00)
        self.assertEqual(cart_item.cart_item_total_no_fee, 0.00)
        self.assertEqual(float(cart_item.cart_item_total), 0.00)
        self.assertEqual(float(cart_item.cart_item_fee), 0.00)
        self.assertEqual(cart_item.discount_code_activated, False)






        # donation_ticket_1 = Ticket.objects.create(
        #     event=event, title="Donation Mega Ticket 1", buyer_price=0.00, min_amount=0, max_amount=10, donation=True, pass_fee=True,
        #     amount_available=500)


        


        

        

        


        
