from datetime import timedelta
import re

from django.db import models
from django.utils import timezone

from smokeyfeet.minishop.exceptions import CartFullError, StockOutError

CART_ITEM_EXPIRY_SECS = 60 * 5  # 5 minutes

PARTNER_RE = re.compile(r"couple|partner", re.IGNORECASE)


class CartManager(models.Manager):
    def from_request(self, request):
        # Get or create cart for request
        cart_id = request.session.get("cart_id", None)
        cart, created = Cart.objects.get_or_create(pk=cart_id)
        if created:
            request.session["cart_id"] = cart.id
        else:
            cart.save()  # Update "updated_at" timestamp

        # Delete all inactive carts
        self.inactive().delete()

        return cart

    def _expiry_time(self):
        return timezone.now() - timedelta(minutes=30)

    def active(self):
        """
        Carts which have not expired
        """
        return self.filter(updated_at__gte=self._expiry_time())

    def inactive(self):
        """
        Carts which have expired
        """
        return self.filter(updated_at__lt=self._expiry_time())


class Cart(models.Model):
    """
    * Stocked items may be added to the cart
    * Adding an item to the cart does not reduce the product stock quantity
    * On checkout the items are validated against available stock
    """

    objects = CartManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_empty(self):
        return self.items.active().count() == 0

    def is_full(self):
        return self.items.active().count() >= 1

    def has_backorder_items(self):
        return any(item.quantity_backorder > 0 for item in self.items.active())

    def get_subtotal(self):
        return sum(item.total_price for item in self.items.active())

    def add_product(self, product, quantity=1):
        if self.is_full():
            raise CartFullError("Cart is full")

        qty = 0
        qty_backorder = 0

        if product.allow_backorder:
            if product.backorder_required(quantity):
                qty_backorder = quantity
            else:
                qty = quantity
        else:
            product.verify_available(quantity)  # raises StockOutError
            qty = quantity

        CartItem.objects.create(
            cart=self,
            product_id=product.id,
            price=product.unit_price,
            quantity=qty,
            quantity_backorder=qty_backorder,
        )

        self.save()  # Update "updated_at" timestamp

    def has_stockout_items(self):
        for item in self.items.active():
            try:
                item.product.verify_stock(item.quantity)
            except StockOutError:
                return True

        return False

    def remove_stockout_items(self):
        for item in self.items.all():
            try:
                item.product.verify_stock(item.quantity)
            except StockOutError:
                item.delete()

    def remove_item_by_id(self, item_id):
        CartItem.objects.filter(cart=self, id=item_id).delete()

    def clear(self):
        """
        Remove all items from cart
        """
        CartItem.objects.filter(cart=self).delete()

    def is_partner_required(self):
        """
        HACK XXX(emiel)
        """
        for item in self.items.active():
            match = PARTNER_RE.search(item.product.name)
            if match is not None:
                return True
        return False


class CartItemQuerySet(models.QuerySet):
    def _expiry_time(self):
        """
        An item may be kept in the cart for a limited duration.
        """
        return timezone.now() - timedelta(seconds=CART_ITEM_EXPIRY_SECS)

    def active(self):
        return self.filter(created_at__gte=self._expiry_time())

    def expired(self):
        return self.filter(created_at__lt=self._expiry_time())


class CartItem(models.Model):
    objects = CartItemQuerySet.as_manager()

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(
        "minishop.Product", on_delete=models.CASCADE, related_name="+"
    )

    quantity = models.PositiveIntegerField()
    quantity_backorder = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.quantity * self.price

    @property
    def expires_at(self):
        return self.created_at + timedelta(seconds=CART_ITEM_EXPIRY_SECS)
