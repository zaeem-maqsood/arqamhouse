from .base import *

from django.core.validators import RegexValidator

from events.models import Event, Ticket



class EventDiscount(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    tickets = models.ManyToManyField(Ticket, blank=True)
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    code = models.CharField(max_length=100, null=True, blank=True, validators=[alphanumeric])
    fixed_amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    percentage_amount = models.PositiveSmallIntegerField(blank=True, null=True)
    use_fixed_amount = models.BooleanField(default=False)
    total_uses = models.PositiveIntegerField(blank=True, null=True)
    used = models.PositiveIntegerField(blank=True, null=True, default=0)
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

    def save(self, *args, **kwargs):
        self._check_if_fixed_amount_or_percentage_amount()
        super().save(*args, **kwargs)

    def get_update_view(self):
        view_name = "events:update_discount"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})
