import factory

from faker import Factory as FakerFactory

faker = FakerFactory.create()


class LunchTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "registration.LunchType"

    sort_order = faker.random_int()


class PassTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "registration.PassType"

    sort_order = faker.random_int()
    data = {}


class RegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "registration.Registration"

    lunch = factory.SubFactory(LunchTypeFactory)
    pass_type = factory.SubFactory(PassTypeFactory)


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "minishop.Cart"


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "minishop.Product"


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "minishop.Order"
