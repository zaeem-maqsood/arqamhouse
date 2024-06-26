from .base import *
import qrcode
from io import BytesIO, StringIO
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from bs4 import BeautifulSoup

from events.models import Event, EventCart, Checkin
from payments.models import Transaction


def pdf_location(instance, filename):
    return "order_pdfs/%s/%s" % (instance.event.house.slug, instance.pk)


def qrcode_location(instance, filename):
    return "order_qrcodes/%s/%s" % (instance.public_id, filename)


def ics_file_location(instance, filename):
    return "order_ics_file/%s/%s" % (instance.public_id, filename)



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
    ics_file = models.FileField(upload_to=ics_file_location, null=True, blank=True)
    code = models.ImageField(upload_to=qrcode_location, max_length=500, blank=True, null=True)
    number = models.PositiveIntegerField(null=True, blank=True, default=0)
    public_id = models.CharField(max_length=150, null=True, blank=True)
    house_created = models.BooleanField(default=False)

    def __str__(self):
        return ("%s" % self.name)


    def set_order_number(self):
        event_orders = EventOrder.objects.filter(event=self.event)
        orders_exist = event_orders.exists()
        if orders_exist:
            latest_order = event_orders.order_by("-created_at")[0]
            self.number = latest_order.number + 1
        else:
            self.number = 1	


    def create_ics_file(self):
        from ics import Calendar, Event
        c = Calendar()
        e = Event()
        e.name = self.event.title
        e.begin = f'{self.event.start}'
        if self.event.end:
            e.end = f'{self.event.end}'
        if self.event.venue_address:
            e.location = f"{self.event.venue_address}"
        e.url = f"https://www.arqamhouse.com/orders/{self.public_id}"
        if self.event.description:
            clean_description = BeautifulSoup(self.event.description)
            e.description = f"{clean_description.text}"
        c.events.add(e)
        file = ContentFile(str(c).encode('utf-8'), f'{self.event.slug}.ics')
        self.ics_file = file


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

        self.create_ics_file()

        super().save(*args, **kwargs)

    def get_order_view(self):
        view_name = "events:order_detail"
        return reverse(view_name, kwargs={"slug": self.event.slug, "public_id": self.public_id})

    def get_public_order_view(self):
        view_name = "order_detail_public"
        return reverse(view_name, kwargs={"public_id": self.public_id})



    
