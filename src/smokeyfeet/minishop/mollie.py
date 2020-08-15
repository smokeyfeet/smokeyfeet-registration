import logging

from django.conf import settings
from django.urls import reverse

from mollie.api.client import Client
from mollie.api.error import Error as MollieError


logger = logging.getLogger(__name__)


def _make_mollie_client():
    mollie_client = Client()
    mollie_client.set_api_key(settings.MOLLIE_API_KEY)
    return mollie_client


def create_payment(request, order):
    redirect_url = request.build_absolute_uri(
        reverse("minishop:order", args=[order.id])
    )

    params = {
        "amount": {"currency": "EUR", "value": float(order.get_subtotal())},
        "description": "Smokey Feet 2017 PP",
        "redirectUrl": redirect_url,
        "metadata": {"order_id": str(order.id)},
    }

    mollie_client = _make_mollie_client()

    logger.info("Creating mollie payment: %s", params)
    try:
        payment = mollie_client.payments.create(params)
    except MollieError as err:
        logger.error("Mollie API call failed: %s", str(err))
        return None
    else:
        logger.info(
            "Order (%s) - New Mollie payment %s @ %s",
            order.id,
            payment["id"],
            payment["amount"],
        )

        return payment


def retrieve_payment(payment_id):
    client = _make_mollie_client()

    try:
        payment = client.payments.get(payment_id)
    except MollieError as err:
        logger.error("Mollie API call failed: %s", str(err))
        return None
    else:
        return payment
