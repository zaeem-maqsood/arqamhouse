from .base import *
import qrcode
from io import BytesIO, StringIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from .events import Event
from .carts import EventCart
from payments.models import Transaction


def pdf_location(instance, filename):
	return "order_pdfs/%s/%s" % (instance.event.house.slug, instance.transaction.payment_id)


def qrcode_location(instance, filename):
	return "order_qrcodes/%s/%s/%s" % (instance.event.house.slug, instance.transaction.payment_id, filename)

class EventOrder(models.Model):

	name = models.CharField(max_length=150, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False, null=False)
	event_cart = models.ForeignKey(EventCart, on_delete=models.CASCADE, blank=False, null=False)
	email = models.EmailField(max_length=300, blank=False, null=False)
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=False, null=False)
	failed = models.BooleanField(default=False)
	refunded = models.BooleanField(default=False)
	note = models.TextField(blank=True, null=True)
	pdf = models.FileField(upload_to=pdf_location, blank=True, null=True)
	code = models.ImageField(upload_to=qrcode_location, blank=True, null=True)

	def __str__(self):
		return ("%s" % self.name)

	def get_order_view(self):
		view_name = "events:order_detail"
		return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})


	def qrcode(self):

		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data('http://google.ca')
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")

		string_io = BytesIO()
		img.save(string_io, format='JPEG')
		img_content = ContentFile(string_io.getvalue(), 'test.jpeg')

		self.code = img_content
		self.save()
		return self