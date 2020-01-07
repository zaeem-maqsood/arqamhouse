from .base import *

from events.models import Event, Ticket


class Checkin(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    tickets = models.ManyToManyField(Ticket, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    exclusive = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


    def _exclusivity(self):
        if self.pk:
            if self.tickets.exists():
                self.exclusive = True
            else:
                self.exclusive = False

    def save(self, *args, **kwargs):
        self._exclusivity()
        super().save(*args, **kwargs)


    def get_attendee_amount(self):
        from events.models import Attendee
        if self.exclusive:
            tickets = self.tickets.all()
            all_attendees = Attendee.objects.filter(order__event=self.event, ticket__in=tickets).order_by('order__created_at')
        else:
            all_attendees = Attendee.objects.filter(order__event=self.event).order_by('order__created_at')

        return all_attendees.count()


    def get_checkin_view(self):
        view_name = "events:checkin"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})

    def get_checkin_update_view(self):
        view_name = "events:checkin_update"
        return reverse(view_name, kwargs={"slug": self.event.slug, "pk": self.id})
