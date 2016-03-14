from datetime import timedelta

from django.db import models
from django.utils import timezone

from .exceptions import CartError, ProductError


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

    @property
    def num_available(self):
        carts = Cart.objects.active()
        items = LineItem.objects.filter(product=self.id, cart__in=carts)
        agg = items.aggregate(qty_sum=models.Sum('quantity'))
        num_in_carts = agg['qty_sum'] or 0
        return self.num_in_stock - num_in_carts

    @property
    def is_available(self):
        self.num_available > 0


class Order(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    amount = models.FloatField(blank=True, default=0.0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class CartManager(models.Manager):

    def from_request(self, request):
        """Fetch cart for request"""
        # Purge any other inactive carts
        self.inactive().delete()

        cart_id = request.session.get("cart_id", None)
        cart, created = Cart.objects.get_or_create(pk=cart_id)
        if created:
            request.session['cart_id'] = cart.id

        return cart

    def _expiry_time(self):
        return timezone.now() - timedelta(minutes=1)

    def active(self):
        "carts which have not expired"
        return self.filter(updated_at__gte=self._expiry_time())

    def inactive(self):
        "carts which have expired"
        return self.filter(updated_at__lt=self._expiry_time())


class Cart(models.Model):

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
            total += (item.quantity * item.price)
        return total

    def add_to_cart(self, product, quantity=1):
        if product.num_available == 0:
            raise ProductError("not available; possibly sold out")
        elif self.is_full:
            raise CartError("cart is full")

        LineItem.objects.create(
                cart=self, product_id=product.id,
                price=product.unit_price, quantity=quantity)

        # Reduce stock
        product.num_in_stock -= 1
        product.save()


class LineItem(models.Model):
    product = models.ForeignKey(Product)
    cart = models.ForeignKey(Cart, related_name="items")
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
