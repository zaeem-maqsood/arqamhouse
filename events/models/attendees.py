from .base import *
import qrcode
from io import BytesIO, StringIO
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

import googlemaps
from core.models import TimestampedModel
from houses.models import House
from events.models import Event, Ticket, EventOrder, EventCartItem, Checkin
from core.constants import genders
from cities_light.models import City, Region, Country
from payments.models import Refund


refund_policies = (
			('standard', 'Standard'),
			('7-days', '7-days'),
			('30-days', '30-days'),
			('no refunds', 'No Refunds')
		)


def qrcode_location(instance, filename):
	return "order_qrcodes/%s/attendee_qr_codes/%s/%s" % (instance.order.public_id, instance.code, filename)
	

class Attendee(TimestampedModel):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=False, null=False)
	ticket_price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	ticket_buyer_price = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	ticket_fee = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
	ticket_pass_fee = models.BooleanField(default=True)
	ticket_refund_policy = models.CharField(max_length=150, choices=refund_policies, default='standard')
	name = models.CharField(max_length=150, null=True, blank=True)
	email = models.EmailField(max_length=120, null=True, blank=True)
	address = models.CharField(max_length=200, blank=True, null=True)
	gender = models.CharField(max_length=20, choices=genders, default='female', null=True, blank=True)
	age = models.PositiveSmallIntegerField(blank=True, null=True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
	active = models.BooleanField(default=True)
	unique_id = models.CharField(max_length=5, null=True, blank=True)
	code = models.ImageField(upload_to=qrcode_location, max_length=500, blank=True, null=True)
	checkins = models.ManyToManyField(Checkin, blank=True)

	def __str__(self):
		return self.name

	def generate_unique_id(self):
		while True:
			unique_id = get_random_string(length=4)
			try:
				Attendee.objects.get(order__event=self.order.event, unique_id=unique_id)
			except:
				break
		self.unique_id = unique_id

	
	def qrcode(self):
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(self.unique_id)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		string_io = BytesIO()
		img.save(string_io, format='JPEG')
		img_content = ContentFile(string_io.getvalue(), 'qrcode.jpeg')
		self.code = img_content

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
			self.generate_unique_id()
			self.update_city_region_country()
			self.qrcode()

		if not self.unique_id:
			self.generate_unique_id()
		
		self.update_city_region_country()

		super().save(*args, **kwargs)

	
	def get_request_for_refund_if_available(self):
		from events.models import EventRefundRequest

		if not self.active:
			return False

		if self.ticket.free:
			return False

		
		try:
			refund_request = EventRefundRequest.objects.get(attendee=self, dismissed=False, processed=False)
			return True
		except:
			return False

		try: 
			refund_request = EventRefundRequest.objects.get(order=self.order, dismissed=False)
			return True
		except:
			return False

		


	def get_refundable_or_not(self):
		from events.models import EventRefundRequest
		event = self.order.event
		policy = self.ticket_refund_policy
		print(policy)

		if not self.active:
			return "Refunded"

		if self.ticket.free:
			return "Free Ticket"


		if policy == 'no refunds':
			return "Refund Not Available"    

		
		try:
			refund_request = EventRefundRequest.objects.get(attendee=self, dismissed=False)
			return "Refund Request Sent!"
		except:

			current_time = timezone.localtime(timezone.now())
			event_start_time = timezone.localtime(event.start)

			if current_time > event_start_time:
				print("Event is done son")
				return "Refund Not Available"
			
			else:

				time_left = event_start_time - current_time
				time_left_days = time_left.days
				time_left_hours = time_left.seconds//3600

				# 30-day policy
				if policy == '30-days':
					if time_left_days < 30:
						return "Refund Not Available"
					else:
						return """<button type="submit" name="Refund" id='Refund' value="%s" class="btn btn--primary">Request Refund</button>""" % (self.id)

				elif policy == '7-days':
					if time_left_days < 7:
						return "Refund Not Available"
					else:
						return """<button type="submit" name="Refund" id='Refund' value="%s" class="btn btn--primary">Request Refund</button>""" % (self.id)

				else:
					if time_left_days > 1:
						return """<button type="submit" name="Refund" id='Refund' value="%s" class="btn btn--primary">Request Refund</button>""" % (self.id)

					else:
						if time_left_hours <= 24:
							return """<button type="submit" name="Refund" id='Refund' value="%s" class="btn btn--primary">Request Refund</button>""" % (self.id)
						else:
							return "Return Not Available"

		
		try:
			refund_request = EventRefundRequest.objects.get(order=self.order, dismissed=False)
			return "Refund Request Sent!"
		except:
			pass



	def get_attendee_view(self):
		view_name = "events:attendee_detail"
		return reverse(view_name, kwargs={"slug": self.order.event.slug, "attendee_id": self.id})



class EventOrderRefund(models.Model):

	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	refund = models.ForeignKey(Refund, on_delete=models.CASCADE, blank=True, null=True)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return (self.order.name)



class EventRefundRequest(models.Model):

	created_at = models.DateTimeField(default=timezone.now)
	order = models.ForeignKey(EventOrder, on_delete=models.CASCADE, blank=False, null=False)
	attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, blank=True, null=True)
	dismissed = models.BooleanField(default=False)
	processed = models.BooleanField(default=False)

	def __str__(self):
		return (self.order.name)

