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


def create_payment(request, registration):
    redirect_url = request.build_absolute_uri(
        (reverse("registration:status", args=[registration.id]))
    )

    params = {
        "amount": {"currency": "EUR", "value": float(registration.amount_due)},
        "description": "Smokey Feet 2017",
        "redirectUrl": redirect_url,
        "metadata": {"registration_id": str(registration.pk)},
    }

    client = _make_mollie_client()

    logger.info("Creating mollie payment: %s", params)
    try:
        payment = client.payments.create(params)
    except MollieError as err:
        logger.error("Mollie API call failed: %s", str(err))
        return None

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
