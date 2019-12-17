from django.test import TestCase
import decimal
from houses.models import House
from payments.models import Transaction, HouseBalance, HouseBalanceLog, Refund, Payout, HousePayment


# Create your tests here.


class PaymentsModelTestCase(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")
        house_balance = HouseBalance.objects.create(house=house, balance=0.00, gross_balance=0.00)
        house_balance_logs = HouseBalanceLog.objects.create(house_balance=house_balance, balance=0.00, opening_balance=True, gross_balance=0.00)

    def test_fee_method(self):
        house = House.objects.get(name="Arqam House")

        transaction = Transaction.objects.create(house=house, name="Zaeem Maqsood")

        transaction.amount = decimal.Decimal(57.80)
        transaction.house_amount = decimal.Decimal(55.00)
        transaction.stripe_amount = decimal.Decimal(1.98)
        transaction.arqam_amount = decimal.Decimal(0.82)

        transaction.payment_id = "ch_1Fq3w4HblWxAI5SaQ1g4palJ"
        transaction.last_four = "4242"
        transaction.brand = "Visa"
        transaction.network_status = "approved_by_network"
        transaction.risk_level = "normal"
        transaction.seller_message = "Payment complete."
        transaction.outcome_type = "authorized"
        transaction.email = "zaeem.maqsood@gmail.com"
        transaction.address_postal_code = "10000"
        transaction.save()
        transaction = Transaction.objects.get(house=house)
        self.assertEqual(transaction.fee(), decimal.Decimal('2.80'))

    def test_refund_fee_method(self):
        house = House.objects.get(name="Arqam House")
        transaction = Transaction.objects.create(house=house, name="Zaeem Maqsood")

        transaction.amount = decimal.Decimal(57.80)
        transaction.house_amount = decimal.Decimal(55.00)
        transaction.stripe_amount = decimal.Decimal(1.98)
        transaction.arqam_amount = decimal.Decimal(0.82)

        transaction.payment_id = "ch_1Fq3w4HblWxAI5SaQ1g4palJ"
        transaction.last_four = "4242"
        transaction.brand = "Visa"
        transaction.network_status = "approved_by_network"
        transaction.risk_level = "normal"
        transaction.seller_message = "Payment complete."
        transaction.outcome_type = "authorized"
        transaction.email = "zaeem.maqsood@gmail.com"
        transaction.address_postal_code = "10000"
        transaction.save()
        transaction = Transaction.objects.get(house=house)
        refund = Refund.objects.create(transaction=transaction, amount=57.80, house_amount=55.00)
        self.assertEqual(refund.fee(), 2.799999999999997)

    def test_house_balance_logs_get_updated_for_transactions(self):

        house = House.objects.get(name="Arqam House")
        house_balance = HouseBalance.objects.get(house=house)
        self.assertEqual(house_balance.balance, 0.00)
        self.assertEqual(house_balance.gross_balance, 0.00)

        # Make a transaction object
        transaction = Transaction.objects.create(house=house, name="Zaeem Maqsood")
        transaction.amount = decimal.Decimal(57.80)
        transaction.house_amount = decimal.Decimal(55.00)
        transaction.stripe_amount = decimal.Decimal(1.98)
        transaction.arqam_amount = decimal.Decimal(0.82)
        transaction.payment_id = "ch_1Fq3w4HblWxAI5SaQ1g4palJ"
        transaction.last_four = "4242"
        transaction.brand = "Visa"
        transaction.network_status = "approved_by_network"
        transaction.risk_level = "normal"
        transaction.seller_message = "Payment complete."
        transaction.outcome_type = "authorized"
        transaction.email = "zaeem.maqsood@gmail.com"
        transaction.address_postal_code = "10000"
        transaction.save()

        # Check balance after the transaction is created
        house_balance = HouseBalance.objects.get(house=house)
        self.assertEqual(house_balance.balance, 55.00)
        self.assertEqual(house_balance.gross_balance, decimal.Decimal('57.80'))
        house_balance_log = HouseBalanceLog.objects.get(house_balance=house_balance, transaction=transaction)
        self.assertEqual(house_balance_log.balance, 55.00)
        self.assertEqual(house_balance_log.gross_balance, decimal.Decimal('57.80'))

        # Make a refund object
        refund = Refund.objects.create(transaction=transaction, amount=57.80, house_amount=55.00)

        # Check the balance after the refund is created
        house_balance = HouseBalance.objects.get(house=house)
        self.assertEqual(house_balance.balance, 0)
        self.assertEqual(house_balance.gross_balance, decimal.Decimal('0.00'))
        house_balance_log = HouseBalanceLog.objects.get(house_balance=house_balance, refund=refund)
        self.assertEqual(house_balance_log.balance, 0.00)
        self.assertEqual(house_balance_log.gross_balance, decimal.Decimal('0.00'))


        # Make another transaction object
        transaction = Transaction.objects.create(house=house, name="Iman Fattah")
        transaction.amount = decimal.Decimal(57.80)
        transaction.house_amount = decimal.Decimal(55.00)
        transaction.stripe_amount = decimal.Decimal(1.98)
        transaction.arqam_amount = decimal.Decimal(0.82)
        transaction.payment_id = "ch_1Fq3w4HblWxAI5SaQ1g4palJ"
        transaction.last_four = "4242"
        transaction.brand = "Visa"
        transaction.network_status = "approved_by_network"
        transaction.risk_level = "normal"
        transaction.seller_message = "Payment complete."
        transaction.outcome_type = "authorized"
        transaction.email = "zaeem.maqsood@gmail.com"
        transaction.address_postal_code = "10000"
        transaction.save()

        # Make a Payout object
        payout = Payout.objects.create(house=house, amount=decimal.Decimal(55.00), processed=True)

        # Check the balance after the payout is created
        house_balance = HouseBalance.objects.get(house=house)
        self.assertEqual(house_balance.balance, 0)
        self.assertEqual(house_balance.gross_balance, decimal.Decimal('0.00'))
        house_balance_log = HouseBalanceLog.objects.get(house_balance=house_balance, payout=payout)
        self.assertEqual(house_balance_log.balance, 0.00)
        self.assertEqual(house_balance_log.gross_balance, decimal.Decimal('0.00'))

        # Make another transaction object
        transaction = Transaction.objects.create(house=house, name="Maria Maqsood")
        transaction.amount = decimal.Decimal(57.80)
        transaction.house_amount = decimal.Decimal(55.00)
        transaction.stripe_amount = decimal.Decimal(1.98)
        transaction.arqam_amount = decimal.Decimal(0.82)
        transaction.payment_id = "ch_1Fq3w4HblWxAI5SaQ1g4palJ"
        transaction.last_four = "4242"
        transaction.brand = "Visa"
        transaction.network_status = "approved_by_network"
        transaction.risk_level = "normal"
        transaction.seller_message = "Payment complete."
        transaction.outcome_type = "authorized"
        transaction.email = "zaeem.maqsood@gmail.com"
        transaction.address_postal_code = "10000"
        transaction.house_payment = True
        transaction.save()

        # Create funds added object
        house_payment = HousePayment.objects.create(transaction=transaction)

        # Check the balance after the payout is created
        house_balance = HouseBalance.objects.get(house=house)
        self.assertEqual(house_balance.balance, 55.00)
        self.assertEqual(house_balance.gross_balance, decimal.Decimal('57.80'))
        house_balance_log = HouseBalanceLog.objects.get(house_balance=house_balance, house_payment=house_payment)
        self.assertEqual(house_balance_log.balance, 55.00)
        self.assertEqual(house_balance_log.gross_balance, decimal.Decimal('57.80'))








