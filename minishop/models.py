from datetime import timedelta
import re
import uuid

from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from .exceptions import CartFullError, StockOutError


CART_ITEM_EXPIRY_SECS = 60 * 5  # 5 minutes
UNPAID_ORDER_EXPIRY_SECS = 60 * 15  # 15 minutes

PARTNER_RE = re.compile(r"couple|partner", re.IGNORECASE)


class ProductManager(models.Manager):

    def in_stock(self):
        return self.filter(num_in_stock__gt=0)


class Product(models.Model):

    objects = ProductManager()

    name = models.CharField(max_length=128)
    description = models.TextField()
    num_in_stock = models.IntegerField(default=0)
    unit_price = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)
    allow_backorder = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

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
        "carts which have not expired"
        return self.filter(updated_at__gte=self._expiry_time())

    def inactive(self):
        "carts which have expired"
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
                cart=self, product_id=product.id,
                price=product.unit_price, quantity=qty,
                quantity_backorder=qty_backorder)

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
        CartItem.objects.filter(cart=self).delete()

    def is_partner_required(self):
        """
        HACK
        """
        for item in self.items.active():
            match = PARTNER_RE.search(item.product.name)
            if match is not None:
                return True
        return False


class CartItemManager(models.Manager):

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

    objects = CartItemManager()

    cart = models.ForeignKey(
            Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    quantity_backorder = models.PositiveIntegerField()
    price = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.quantity * self.price

    @property
    def expires_at(self):
        return self.created_at + timedelta(seconds=CART_ITEM_EXPIRY_SECS)


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
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)

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
                    price=cart_item.price)

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
    order = models.ForeignKey(
            Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
            Product, on_delete=models.SET_NULL, blank=True, null=True)

    product_name = models.CharField(max_length=128, default="{unknown}")
    quantity = models.PositiveIntegerField()
    quantity_backorder = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    @property
    def total_price(self):
        return self.quantity * self.price


class Payment(models.Model):
    order = models.ForeignKey(
            Order, on_delete=models.CASCADE, related_name="payments")

    mollie_payment_id = models.CharField(max_length=64, unique=True)

    amount = models.DecimalField(
            max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
