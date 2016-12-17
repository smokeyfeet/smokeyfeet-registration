import logging

from django.conf import settings
from django.core.urlresolvers import reverse

import Mollie


logger = logging.getLogger(__name__)


def _make_mollie_client():
    mollie = Mollie.API.Client()
    mollie.setApiKey(settings.MOLLIE_API_KEY)
    return mollie


def create_payment(request, registration):
    redirect_url = request.build_absolute_uri(
            (reverse("registration:status", args=[registration.id])))

    params = {
        "amount": float(registration.amount_due),
        "description": "Smokey Feet 2017",
        "redirectUrl": redirect_url,
        "metadata": {
            "registration_id": str(registration.pk)
        }
    }

    client = _make_mollie_client()

    logger.info("Creating mollie payment: %s", params)
    try:
        payment = client.payments.create(params)
    except Mollie.API.Error as err:
        logger.error("Mollie API call failed: %s", err.message)
        return None

    return payment


def retrieve_payment(payment_id):
    client = _make_mollie_client()

    try:
        payment = client.payments.get(payment_id)
    except Mollie.API.Error as err:
        logger.error("Mollie API call failed: %s", err.message)
        return None
    else:
        return payment
