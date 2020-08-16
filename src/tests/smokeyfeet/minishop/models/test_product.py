import pytest

from smokeyfeet.minishop.models import Product


@pytest.mark.django_db
def test_product_str(product_factory):
    product = product_factory(name="quux")
    assert str(product) == "quux"


@pytest.mark.django_db
def test_in_stock(product_factory):
    p0 = product_factory(num_in_stock=0)
    assert not p0.in_stock

    p1 = product_factory(num_in_stock=10)
    assert p1.in_stock


@pytest.mark.django_db
def test_manager_in_stock(product_factory):
    product_factory(num_in_stock=0)
    product_factory(num_in_stock=10)

    qs = Product.objects.in_stock()
    assert len(qs) == 1
    assert qs[0].num_in_stock == 10
