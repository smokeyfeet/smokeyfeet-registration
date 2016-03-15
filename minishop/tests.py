from django.test import TestCase

from .exceptions import CartFullError, StockOutError
from .models import Cart, Product


class TestProduct(TestCase):

    def test_str(self):
        p = Product.objects.create(name="quux")
        self.assertEqual(str(p), "quux")

    def test_in_stock(self):
        p0 = Product.objects.create(num_in_stock=0)
        self.assertFalse(p0.in_stock)

        p1 = Product.objects.create(num_in_stock=10)
        self.assertTrue(p1.in_stock)


class TestProductManager(TestCase):

    def test_in_stock(self):
        Product.objects.create(num_in_stock=0)
        Product.objects.create(num_in_stock=10)

        ps = Product.objects.in_stock()
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0].num_in_stock, 10)


class TestCart(TestCase):

    def test_str(self):
        pass

    def test_add_product_success(self):
        product = Product.objects.create(num_in_stock=1)

        cart = Cart.objects.create()
        cart.add_product(product)

    def test_add_product_unavailable(self):
        product = Product.objects.create(num_in_stock=0)

        cart = Cart.objects.create()

        with self.assertRaises(StockOutError):
            cart.add_product(product)

    def test_add_product_cart_full(self):
        product = Product.objects.create(num_in_stock=20)

        cart = Cart.objects.create()
        cart.add_product(product)

        with self.assertRaises(CartFullError):
            cart.add_product(product)