import datetime
import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum
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
    unit_price = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    data = JSONField()

    def __str__(self):
        s  = "{} - €{}".format(self.name, self.unit_price)
        if self.video_audition_required:
            s += " - video audition"
        return s

    @property
    def video_audition_required(self):
        return self.data.get("video_audition_required", False)

    class Meta:
        ordering = ['sort_order']


class LunchType(models.Model):

    name = models.CharField(max_length=64)
    sort_order = models.PositiveIntegerField()
    unit_price = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return "{} - €{}".format(self.name, self.unit_price)

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

    dance_role = models.CharField(
            max_length=32, choices=DANCE_ROLES, default=ROLE_LEADER)

    residing_country = CountryField()

    pass_type = models.ForeignKey(PassType, on_delete=models.PROTECT)
    workshop_partner_name = models.CharField(max_length=128, blank=True)
    workshop_partner_email = models.EmailField(blank=True)

    lunch = models.ForeignKey(LunchType, on_delete=models.PROTECT)

    crew_remarks = models.TextField(max_length=4096, blank=True)

    total_price = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, {} ({})".format(
                self.last_name, self.first_name, self.email)

    @property
    def is_accepted(self):
        return self.accepted_at is not None

    @property
    def payment_due_date(self):
        return self.accepted_at + datetime.timedelta(days=7)

    @property
    def video_audition_due_date(self):
        return self.accepted_at + datetime.timedelta(days=21)

    @property
    def amount_due(self):
        return self.total_price

    @property
    def amount_paid(self):
        result = self.payment_set.aggregate(amount_paid=Sum("amount"))
        return result.get("amount_paid") or 0.0

    @property
    def paid_in_full(self):
        return self.amount_paid >= self.amount_due

    def fixate_price(self):
        self.total_price = self.pass_type.unit_price + self.lunch.unit_price

    def log_interaction(self, description):
        Interaction.objects.create(registration=self, description=description)


class Payment(models.Model):

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    mollie_payment_id = models.CharField(
            max_length=64, unique=True, null=True, blank=True)

    amount = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Interaction(models.Model):

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    description = models.TextField(max_length=4096, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
