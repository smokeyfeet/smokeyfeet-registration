import pytest


@pytest.mark.django_db
def test_return_to_stock(order_factory, product_factory):
    product = product_factory(num_in_stock=10, unit_price=20)

    order = order_factory()
    order.items.create(product=product, quantity=1, price=20)

    order.return_to_stock()

    product.refresh_from_db()
    assert product.num_in_stock == 11


@pytest.mark.django_db
def test_get_subtotal(order_factory, product_factory):
    product = product_factory(num_in_stock=10, unit_price=20)

    order = order_factory()
    order.items.create(product=product, quantity=3, price=22.5)

    assert order.get_subtotal() == 67.5


@pytest.mark.django_db
def test_get_amount_paid(order_factory):
    order = order_factory()
    order.payments.create(mollie_payment_id="pmt1", amount=22.5)
    order.payments.create(mollie_payment_id="pmt2", amount=22.5)

    assert order.get_amount_paid() == 45.0


@pytest.mark.django_db
def test_is_paid(order_factory, product_factory):
    product = product_factory(num_in_stock=10, unit_price=20)

    order = order_factory()
    order.items.create(product=product, quantity=1, price=22.5)

    assert not order.is_paid()

    order.payments.create(mollie_payment_id="pmt1", amount=22.5)
    assert order.is_paid()
