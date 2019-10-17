from .base import *

from django.core.validators import RegexValidator
from django.db.models.signals import pre_save, post_save

from events.models import Event, Ticket



class EventDiscount(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    tickets = models.ManyToManyField(Ticket, blank=True)
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    code = models.CharField(max_length=100, null=True, blank=True, validators=[alphanumeric])
    fixed_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    percentage_amount = models.PositiveSmallIntegerField(blank=True, null=True)
    use_fixed_amount = models.BooleanField(default=False)
    total_uses = models.PositiveIntegerField(blank=True, null=True, default=1000)
    used = models.PositiveIntegerField(blank=True, null=True, default=0)
    finished = models.BooleanField(default=False)
    start = models.DateTimeField(blank=True, null=True, default=timezone.now)
    end = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


    def __str__(self):
        return self.code

    def _check_if_fixed_amount_or_percentage_amount(self):
        fixed_amount = self.fixed_amount
        if fixed_amount:
            self.use_fixed_amount = True
        else:
            self.use_fixed_amount = False

    def percentage_color(self):
        ratio = self.used / self.total_uses
        if ratio <= 0.5:
            return "bg-success"
        elif ratio > 0.50 and ratio <= 0.70:
            return ""
        elif ratio > 0.70 and ratio <= 0.90:
            return "bg-danger"
        else:
            return "bg-danger"

    def percentage_sold(self):
        ratio = self.used / self.total_uses
        return "{0:.0f}%".format(ratio * 100)

    def save(self, *args, **kwargs):
        self._check_if_fixed_amount_or_percentage_amount()
        super().save(*args, **kwargs)

    def get_update_view(self):
        view_name = "events:update_discount"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})




def discount_pre_save_reciever(sender, instance, *args, **kwargs):
    
    # Set the discount to finished
	if instance.used == instance.total_uses:
		instance.finished = True

pre_save.connect(discount_pre_save_reciever, sender=EventDiscount)
