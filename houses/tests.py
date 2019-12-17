
from django.test import TestCase
from houses.models import House
from payments.models import HouseBalance, HouseBalanceLog

# Create your tests here.


class HouseModelTestCase(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")
        house_balance = HouseBalance.objects.create(house=house, balance=0.00, gross_balance=0.00)
        house_balance_logs = HouseBalanceLog.objects.create(house_balance=house_balance, balance=0.00, opening_balance=True, gross_balance=0.00)

    def test_house_return_name(self):
        house = House.objects.get(name="Arqam House")
        self.assertEqual(house.__str__(), 'Arqam House')

    def test_house_slug(self):
        house = House.objects.get(name="Arqam House")
        self.assertEqual(house.slug, 'arqam-house')

    def test_address_entered_field_gets_updated(self):
        house = House.objects.get(name="Arqam House")
        from cities_light.models import City, Region, Country
        country = Country.objects.create(continent="North America", name="Canada")
        region = Region.objects.create(country=country, name="Ontario")
        city = City.objects.create(country=country, region=region, name="Ajax")
        address = "47 Denny Street Ajax, Ontario"
        postal_code = "L1Z0S3"

        house.country = country
        house.region = region
        house.city = city
        house.address = address
        house.postal_code = postal_code
        house.save()

        self.assertEqual(house.address_entered, True)

