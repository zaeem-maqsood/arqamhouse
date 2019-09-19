from .base import *

import googlemaps
from core.models import TimestampedModel
from events.models import Ticket, EventOrder, EventCartItem
from core.constants import genders
from cities_light.models import City, Region, Country
from payments.models import Refund


class Attendee(TimestampedModel):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	name = models.CharField(max_length=150, null=True, blank=True)
	email = models.EmailField(max_length=120, null=True, blank=True)
	address = models.CharField(max_length=200, blank=True, null=True)
	gender = models.CharField(max_length=20, choices=genders, default='female', null=True, blank=True)
	age = models.PositiveSmallIntegerField(blank=True, null=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	def update_city_region_country(self):
		api = settings.GOOGLE_MAPS_API
		gmaps = googlemaps.Client(key=api)

		if self.address:
			# Geocoding an address
		
			geocode_result = gmaps.geocode(self.address)

			city = None
			region = None

			data = geocode_result[0]

			# Extract data from geocode_result. unfortunatly we cannot pinpoint exactly 
			# where the city or region field is, thats why im loopiing over things like a fool 
			# to find out where the region or city value is. On top of that, i want the sublocality 
			# if it is available
			for address_component in data['address_components']:
				for address_component_key, address_component_value in address_component.items():
					if address_component_key == 'types':
						for types_value in address_component_value:
							if types_value == "administrative_area_level_1":
								region = address_component['long_name']
							
							if types_value == "locality":
								if not city:
									city = address_component['long_name']

							if types_value == "sublocality":
								city = address_component['long_name']

		
			country = Country.objects.get(name='Canada')
			self.country = country
			
			try:
				region = Region.objects.get(country=country, name=region)
				city = City.objects.get(country=country, region=region, name=city)
				self.region = region
				self.city = city
			except Exception as e:
				print(e)			
			
		return self.address

	def save(self, *args, **kwargs):
		if not self.pk:
			self.update_city_region_country()
		
		self.update_city_region_country()

		super().save(*args, **kwargs)


	def get_attendee_view(self):
		view_name = "events:attendee_detail"
		return reverse(view_name, kwargs={"slug": self.order.event.slug, "attendee_id": self.id})



class EventOrderRefund(models.Model):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	refund = models.ForeignKey(Refund, on_delete=models.CASCADE, blank=True, null=True)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return (self.order.name)


