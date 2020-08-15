from django.db import models

from smokeyfeet.minishop.exceptions import StockOutError

from .cart import CartItem


class ProductQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(num_in_stock__gt=0)


class Product(models.Model):
    class Meta:
        ordering = ["name"]

    objects = ProductQuerySet.as_manager()

    name = models.CharField(max_length=128)

    description = models.TextField()

    num_in_stock = models.IntegerField(default=0)

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    allow_backorder = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.num_in_stock > 0

    def get_quantity_in_carts(self):
        active_items = CartItem.objects.active().filter(product=self)
        return sum(item.quantity for item in active_items)

    def get_quantity_available(self):
        return self.num_in_stock - self.get_quantity_in_carts()

    def purchasable(self):
        return self.get_quantity_available() > 0

    def backorder_required(self, quantity):
        return self.get_quantity_available() < quantity

    def verify_available(self, quantity):
        if quantity < 0:
            raise ValueError("Quantity may not be negative")

        if self.get_quantity_available() < quantity:
            raise StockOutError("Product unavailable")

    def verify_stock(self, quantity):
        if quantity < 0:
            raise ValueError("Quantity may not be negative")

        if self.num_in_stock < quantity:
            raise StockOutError("Out of stock")
