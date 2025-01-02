import pytest
from pytest_factoryboy import register

from tests.factories import CartFactory
from tests.factories import LunchTypeFactory
from tests.factories import OrderFactory
from tests.factories import PassTypeFactory
from tests.factories import ProductFactory
from tests.factories import RegistrationFactory

# registration
register(RegistrationFactory)
register(LunchTypeFactory)
register(PassTypeFactory)

# minishop
register(CartFactory)
register(OrderFactory)
register(ProductFactory)


@pytest.fixture
def authenticated_user(django_user_model, client):
    user = django_user_model.objects.create_user("bob")
    client.force_login(user)
    return user
