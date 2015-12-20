from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from hashids import Hashids


WORKSHOP_LEVELS = [
        ('drums', 'Drums'),
        ('saxophone', 'Saxophone'),
        ('bass', 'Bass'),
        ('trumpet', 'Trumpet'),
        ('piano', 'Piano')]


class Registration(models.Model):
    first_names = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    is_lead = models.BooleanField()

    telephone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=128, blank=True)

    workshop_level = models.CharField(max_length=32,
            choices=WORKSHOP_LEVELS, blank=True)
    workshop_partner = models.CharField(max_length=128, blank=True)

    wants_lunch = models.BooleanField(default=False)

    # Mollie
    mollie_status = models.CharField(max_length=64, default="foo")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    @property
    def ref(self):
        return Hashids.encode(self.id) if self.id is not None else ''

    @property
    def amount_due(self):
        return 10.00


class MolliePayment(models.Model):
    registration_id = models.ForeignKey(Registration)
    raw_payment = JSONField()


class Mail(models.Model):
    registration = models.ForeignKey(Registration)
    sent_at = models.DateTimeField()
    body = models.TextField()
