from datetime import timedelta
import uuid

from django.db import models
from django.db.models import Sum
from django.urls import reverse


UNPAID_ORDER_EXPIRY_SECS = 60 * 15  # 15 minutes


class Order(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)

    partner_name = models.CharField(max_length=128, blank=True)
    partner_email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {} <{}>".format(self.first_name, self.last_name, self.email)

    def get_absolute_url(self):
        return reverse("minishop:order", args=[str(self.id)])

    def get_subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def get_amount_paid(self):
        result = self.payments.aggregate(amount_paid=Sum("amount"))
        return result.get("amount_paid") or 0.0

    def is_paid(self):
        return self.get_amount_paid() >= self.get_subtotal()

    def add_items_from_cart(self, cart):
        for cart_item in cart.items.active():
            order_item = self.items.create(
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                quantity_backorder=cart_item.quantity_backorder,
                price=cart_item.price,
            )

            # Reduce product stock
            order_item.product.num_in_stock -= order_item.quantity
            order_item.product.save()

    def has_backorder_items(self):
        return any(item.quantity_backorder > 0 for item in self.items.all())

    def return_to_stock(self):
        """race condition"""
        for order_item in self.items.all():
            if order_item.product is not None:
                order_item.product.num_in_stock += order_item.quantity
                order_item.product.save()

    def expires_at(self):
        return self.created_at + timedelta(seconds=UNPAID_ORDER_EXPIRY_SECS)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "minishop.Product", on_delete=models.SET_NULL, blank=True, null=True
    )

    product_name = models.CharField(max_length=128, default="{unknown}")
    quantity = models.PositiveIntegerField()
    quantity_backorder = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    @property
    def total_price(self):
        return self.quantity * self.price
