import datetime as dt

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django_countries.fields import CountryField
from hashids import Hashids

from Mollie.API import Payment


class PassType(models.Model):
    PASS_PARTY = 'party'
    PASS_FULL = 'full'
    PASS_TYPES = [
            (PASS_PARTY, 'Party Pass'),
            (PASS_FULL, 'Full Pass')]

    type = models.CharField(max_length=32, choices=PASS_TYPES)
    name = models.CharField(max_length=64)
    order = models.PositiveIntegerField()
    num_offered = models.PositiveIntegerField()
    video_audition_required = models.BooleanField(default=False)
    price = models.FloatField()

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['order']


class CompetitionType(models.Model):
    name = models.CharField(max_length=64)
    num_offered = models.PositiveIntegerField()
    require_partner = models.BooleanField(default=False)

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class VolunteerType(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=2048)
    num_offered = models.PositiveIntegerField()
    refund_amount = models.FloatField()

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['name']


class Registration(models.Model):
    LUNCH_PRICE = 15.00

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

    residing_country = CountryField()

    pass_type = models.ForeignKey(PassType)
    workshop_partner_name = models.CharField(max_length=128, blank=True)
    workshop_partner_email = models.EmailField(blank=True)

    competitions = models.ManyToManyField(CompetitionType, blank=True)
    strictly_partner = models.CharField(max_length=128, blank=True)

    volunteering_for = models.ManyToManyField(VolunteerType, blank=True)

    include_lunch = models.BooleanField(default=False)
    diet_requirements = models.TextField(max_length=140, blank=True)

    crew_remarks = models.TextField(max_length=4096, blank=True)

    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    payment_reminder_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return "<{}:{}>".format(type(self).__name__, self.id)

    def __str__(self):
        return "{}, {} ({})".format(self.last_name, self.first_name,
                self.email)

    @property
    def ref(self):
        assert self.id is not None
        hashids = Hashids()
        return hashids.encode(self.id)

    @property
    def amount_due(self):
        if self.include_lunch:
            return self.pass_type.price + self.LUNCH_PRICE
        else:
            return self.pass_type.price

    @property
    def is_party_pass(self):
        return self.pass_type.type == PassType.PASS_PARTY

    @property
    def is_full_pass(self):
        return self.pass_type.type == PassType.PASS_FULL

    @property
    def is_accepted(self):
        return self.accepted_at is not None

    @property
    def is_completed(self):
        return self.completed_at is not None

    @property
    def amount_paid(self):
        return self.molliepayment_set.filter(
            mollie_status=Payment.STATUS_PAID).aggregate(amount_paid=Sum('mollie_amount'))['amount_paid']

    @property
    def due_date(self):
        return self.accepted_at + dt.timedelta(days=14)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(Registration, self).save(*args, **kwargs)


class MolliePayment(models.Model):
    registration = models.ForeignKey(Registration)

    mollie_id = models.CharField(max_length=64, unique=True)
    mollie_amount = models.FloatField()
    mollie_status = models.CharField(max_length=32,
            default=Payment.STATUS_OPEN)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
