from datetime import timedelta

from Mollie.API import Payment
from django.db import models
from django.utils import timezone

from .exceptions import CartFullError, StockOutError


class ProductManager(models.Manager):

    def in_stock(self):
        return self.filter(num_in_stock__gt=0)


class Product(models.Model):

    objects = ProductManager()

    name = models.CharField(max_length=128)
    description = models.TextField()
    num_in_stock = models.PositiveIntegerField(default=0)
    unit_price = models.FloatField(default=0)

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.num_in_stock > 0

    def verify_stock(self, quantity):
        if quantity < 0:
            raise ValueError("Quantity may not be negative")

        if self.num_in_stock < quantity:
            raise StockOutError()


class Order(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    amount = models.FloatField(blank=True, default=0.0)

    mollie_status = models.CharField(
            max_length=32, default=Payment.STATUS_OPEN)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)


class CartManager(models.Manager):

    def from_request(self, request):
        # Get or create cart for request
        cart_id = request.session.get("cart_id", None)
        cart, created = Cart.objects.get_or_create(pk=cart_id)
        if created:
            request.session['cart_id'] = cart.id
        else:
            cart.updated_at = timezone.now()
            cart.save()

        # Purge any other inactive carts
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

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def is_empty(self):
        return self.items.count() == 0

    @property
    def is_full(self):
        return self.items.count() >= 1

    @property
    def amount_due(self):
        total = 0.0
        for item in self.items.all():
            total += item.total_price
        return total

    def add_product(self, product, quantity=1, verify_quantity=True):
        if self.is_full:
            raise CartFullError("Cart is full")

        if verify_quantity:
            product.verify_stock(quantity)  # raises StockOutError

        LineItem.objects.create(
                cart=self, product_id=product.id,
                price=product.unit_price, quantity=quantity)

        self.updated_at = timezone.now()
        self.save()

    def has_stockout_items(self):
        for item in self.items.all():
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

    def remove_from_cart(self, product):
        LineItem.objects.filter(cart=self, product=product).delete()

    def clear(self):
        LineItem.objects.filter(cart=self).delete()


class LineItem(models.Model):
    product = models.ForeignKey(Product)
    cart = models.ForeignKey(Cart, related_name="items")
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def total_price(self):
        return self.quantity * self.price
