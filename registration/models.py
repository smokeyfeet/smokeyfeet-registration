import uuid
from decimal import Decimal

from django.db import models
from django_countries.fields import CountryField


class PassType(models.Model):

    PASS_PARTY = 'party'
    PASS_FULL = 'full'
    PASS_TYPES = [
            (PASS_PARTY, 'Party Pass'),
            (PASS_FULL, 'Full Pass')]

    type = models.CharField(max_length=32, choices=PASS_TYPES)
    name = models.CharField(max_length=64)
    active = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField()
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2,
            default=0)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['sort_order']


class LunchType(models.Model):

    name = models.CharField(max_length=64)
    sort_order = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2,
            default=0)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ['sort_order']


class Registration(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)

    ROLE_LEADER = 'leader'
    ROLE_FOLLOWER = 'follower'
    DANCE_ROLES = [
            (ROLE_LEADER, 'Leader'),
            (ROLE_FOLLOWER, 'Follower')]

    dance_role = models.CharField(max_length=32, choices=DANCE_ROLES,
            default=ROLE_LEADER)

    residing_country = CountryField()

    pass_type = models.ForeignKey(PassType, on_delete=models.PROTECT)
    workshop_partner_name = models.CharField(max_length=128, blank=True)
    workshop_partner_email = models.EmailField(blank=True)

    lunch = models.ForeignKey(LunchType, on_delete=models.PROTECT, null=True)

    crew_remarks = models.TextField(max_length=4096, blank=True)

    payment_status = models.CharField(max_length=16)
    payment_status_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, {} ({})".format(self.last_name, self.first_name,
                self.email)

    @property
    def amount_due(self):
        # Hack
        return 34.0

        if self.lunch != LUNCH_NONE:
            return self.pass_type.unit_price + Decimal.from_float(15.0)
        else:
            return self.pass_type.unit_price

    @property
    def is_party_pass(self):
        return self.pass_type.type == PassType.PASS_PARTY

    @property
    def is_full_pass(self):
        return self.pass_type.type == PassType.PASS_FULL

    @property
    def is_accepted(self):
        return True # HACK
        return self.accepted_at is not None

    def is_paid(self):
        return self.payment_status == "paid"


class RegistrationStatus(models.Model):

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    STATUS_QUEUED = 'queued'
    STATUS_ACCEPTED = 'accepted'
    STATUS_PAYMENT_CREATED = 'payment_created'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = [
            (STATUS_QUEUED, 'Queued'),
            (STATUS_ACCEPTED, 'Accepted'),
            (STATUS_PAID, 'Paid')]

    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    status_at = models.DateTimeField(auto_now_add=True)
