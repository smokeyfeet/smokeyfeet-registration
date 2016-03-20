from datetime import timedelta
import uuid

from Mollie.API import Payment
from django.core.urlresolvers import reverse
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

    class Meta:
        ordering = ['name']

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
    def total_due(self):
        total = 0.0
        for item in self.items.all():
            total += item.total_price
        return total

    def add_product(self, product, quantity=1, verify_quantity=True):
        if self.is_full:
            raise CartFullError("Cart is full")

        if verify_quantity:
            product.verify_stock(quantity)  # raises StockOutError

        CartItem.objects.create(
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

    def remove_item_by_id(self, item_id):
        try:
            item_id = int(item_id)
        except ValueError:
            return

        try:
            item = CartItem.objects.filter(cart=self, id=item_id)
        except CartItem.DoesNotExist:
            return
        else:
            item.delete()

    def clear(self):
        CartItem.objects.filter(cart=self).delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items")
    product = models.ForeignKey(Product)

    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def total_price(self):
        return self.quantity * self.price


class Order(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)

    mollie_payment_id = models.CharField(max_length=64, unique=True)
    mollie_payment_status = models.CharField(
            max_length=32, default=Payment.STATUS_OPEN)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)

    def get_absolute_url(self):
        return reverse('order', args=[str(self.id)])

    @property
    def total_due(self):
        total = 0.0
        for item in self.items.all():
            total += item.total_price
        return total

    def add_items_from_cart(self, cart, verify_stock=True):
        for cart_item in cart.items.all():
            if verify_stock:
                cart_item.product.verify_stock(cart_item.quantity)
            order_item = self.items.create(
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    price=cart_item.price)

            # Reduce product stock
            order_item.product.num_in_stock -= order_item.quantity
            order_item.product.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items")
    product = models.ForeignKey(
            Product, models.SET_NULL, blank=True, null=True)

    product_name = models.CharField(max_length=128, default="{unknown}")
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s" % (self.product_name,)

    @property
    def total_price(self):
        return self.quantity * self.price
