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


class CompetitionType(models.Model):
    name = models.CharField(max_length=64)
    num_offered = models.PositiveIntegerField()

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}".format(self.name)


class VolunteerType(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=2048)
    num_offered = models.PositiveIntegerField()
    refund_amount = models.FloatField()

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
    residing_country = models.CharField(max_length=128, blank=True)

    pass_type = models.ForeignKey(PassType)
    workshop_partner = models.CharField(max_length=128, blank=True)

    competitions = models.ManyToManyField(CompetitionType, blank=True)
    strictly_partner = models.CharField(max_length=128, blank=True)

    volunteering_for = models.ManyToManyField(VolunteerType, blank=True)

    include_lunch = models.BooleanField(default=False)
    diet_requirements = models.TextField(max_length=140, blank=True)

    crew_remarks = models.TextField(max_length=4096, blank=True)

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
