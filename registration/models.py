from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from hashids import Hashids


DANCE_ROLES = [
        ('leader', 'Leader'),
        ('follower', 'Follower')]

PASS_TYPES = [
        ('party', 'Party'),
        ('ws_drums', 'Workshop: Drums'),
        ('ws_saxophone', 'Workshop: Saxophone'),
        ('ws_bass', 'Workshop: Bass'),
        ('ws_trumpet_piano', 'Workshop: Trumpet/Piano')]


class Registration(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    dance_role = models.CharField(max_length=32, choices=DANCE_ROLES)

    telephone = models.CharField(max_length=32, blank=True)
    country_of_residence = models.CharField(max_length=128, blank=True)

    pass_type = models.CharField(max_length=32, choices=PASS_TYPES)
    workshop_partner = models.CharField(max_length=128, blank=True)

    wants_volunteer = models.BooleanField(default=False)
    wants_lunch = models.BooleanField(default=False)

    # Mollie
    mollie_status = models.CharField(max_length=64, default="foo")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    @property
    def ref(self):
        hashids = Hashids()
        return hashids.encode(self.id) if self.id is not None else ''

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
