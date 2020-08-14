from django.db import models


class Payment(models.Model):
    registration = models.ForeignKey(
        "registration.Registration", on_delete=models.CASCADE
    )

    mollie_payment_id = models.CharField(
        max_length=64, unique=True, null=True, blank=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
