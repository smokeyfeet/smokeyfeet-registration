import pytest
from pytest_factoryboy import register

from tests.factories import (
    RegistrationFactory,
    LunchTypeFactory,
    PassTypeFactory,
    CartFactory,
    OrderFactory,
    ProductFactory,
)

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
