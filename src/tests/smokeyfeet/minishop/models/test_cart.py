import pytest

from smokeyfeet.minishop.exceptions import CartFullError, StockOutError


@pytest.mark.django_db
def test_add_product_success(cart, product_factory):
    product = product_factory(num_in_stock=10)
    cart.add_product(product)

    assert cart.items.count() == 1


@pytest.mark.django_db
def test_add_product_unavailable(cart, product_factory):
    product = product_factory(num_in_stock=0)

    with pytest.raises(StockOutError):
        cart.add_product(product)


@pytest.mark.django_db
def test_add_product_cart_full(cart, product_factory):
    product = product_factory(num_in_stock=20)

    cart.add_product(product)

    with pytest.raises(CartFullError):
        cart.add_product(product)


@pytest.mark.django_db
def test_clear(cart, product_factory):
    product = product_factory(num_in_stock=20)

    cart.add_product(product)

    assert cart.items.count() == 1
    cart.clear()
    assert cart.items.count() == 0


@pytest.mark.django_db
def test_get_subtotal(cart, product_factory):
    product = product_factory(num_in_stock=20, unit_price=15.50)

    cart.add_product(product, quantity=3)

    assert cart.get_subtotal() == 46.5
