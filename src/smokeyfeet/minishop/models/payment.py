from django.db import models


class Payment(models.Model):
    order = models.ForeignKey(
        "minishop.Order", on_delete=models.CASCADE, related_name="payments"
    )

    mollie_payment_id = models.CharField(max_length=64, unique=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
