from .base import *
import qrcode
from io import BytesIO, StringIO
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from .events import Event
from .carts import EventCart
from payments.models import Transaction


def pdf_location(instance, filename):
	return "order_pdfs/%s/%s" % (instance.event.house.slug, instance.pk)


def qrcode_location(instance, filename):
	return "order_qrcodes/%s/%s" % (instance.public_id, filename)



class EventOrder(models.Model):

	name = models.CharField(max_length=150, null=True, blank=True)
	created_at = models.DateTimeField(default=timezone.now)
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	event_cart = models.ForeignKey(EventCart, on_delete=models.CASCADE, blank=False, null=False)
	email = models.EmailField(max_length=300, blank=False, null=False)
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
	failed = models.BooleanField(default=False)
	partial_refund = models.BooleanField(default=False)
	refunded = models.BooleanField(default=False)
	note = models.TextField(blank=True, null=True)
	pdf = models.FileField(upload_to=pdf_location, blank=True, null=True)
	code = models.ImageField(upload_to=qrcode_location, max_length=500, blank=True, null=True)
	number = models.PositiveIntegerField(null=True, blank=True, default=0)
	public_id = models.CharField(max_length=150, null=True, blank=True)
	house_created = models.BooleanField(default=False)

	def __str__(self):
		return ("%s" % self.name)


	def set_order_number(self):
		print("Testing order numbers")
		event_orders = EventOrder.objects.filter(event=self.event)
		print(event_orders)
		orders_exist = event_orders.exists()
		print(orders_exist)
		if orders_exist:
			print("Yes exits")
			latest_order = event_orders.order_by("-created_at")[0]
			print(latest_order)
			self.number = latest_order.number + 1
		else:
			print("No exists")
			self.number = 1		


	def qrcode(self):
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data('https://www.arqamhouse.com/orders/%s/' % (self.public_id))
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		string_io = BytesIO()
		img.save(string_io, format='JPEG')
		img_content = ContentFile(string_io.getvalue(), 'qrcode.jpeg')
		self.code = img_content

	
	def generate_public_id(self):
		while True:
			public_id = get_random_string(length=32)
			try:
				EventOrder.objects.get(public_id=public_id)
			except:
				break
		self.public_id = public_id
		


	def save(self, *args, **kwargs):
		if not self.pk:
			self.generate_public_id()
			self.qrcode()
			self.set_order_number()

		super().save(*args, **kwargs)

	def get_order_view(self):
		view_name = "events:order_detail"
		return reverse(view_name, kwargs={"slug": self.event.slug, "public_id": self.public_id})


	
