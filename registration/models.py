from django.db import models
from django.utils import timezone
from hashids import Hashids

from Mollie.API import Payment


class PassType(models.Model):
    name = models.CharField(max_length=64)
    num_offered = models.PositiveIntegerField()
    price = models.FloatField()

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}".format(self.name)


class Registration(models.Model):
    ROLE_LEADER = 'leader'
    ROLE_FOLLOWER = 'follower'
    DANCE_ROLES = [
            (ROLE_LEADER, 'Leader'),
            (ROLE_FOLLOWER, 'Follower')]

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    dance_role = models.CharField(max_length=32, choices=DANCE_ROLES,
            default=ROLE_LEADER)

    telephone = models.CharField(max_length=32, blank=True)
    country_of_residence = models.CharField(max_length=128, blank=True)

    pass_type = models.ForeignKey(PassType)
    workshop_partner = models.CharField(max_length=128, blank=True)

    wants_volunteer = models.BooleanField(default=False)
    wants_lunch = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}, {} ({})".format(self.last_name, self.first_name, self.email)

    @property
    def ref(self):
        assert self.id is not None
        hashids = Hashids()
        return hashids.encode(self.id)

    @property
    def amount_due(self):
        return self.pass_type.price


class MolliePayment(models.Model):
    registration = models.ForeignKey(Registration)

    mollie_id = models.CharField(max_length=64, unique=True)
    mollie_status = models.CharField(max_length=32,
            default=Payment.STATUS_OPEN)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
