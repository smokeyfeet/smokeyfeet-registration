import logging

from django.conf import settings
from django.core.urlresolvers import reverse

import Mollie

from .models import MolliePayment
from .utils import make_token


logger = logging.getLogger(__name__)


def _make_mollie_client():
    mollie = Mollie.API.Client()
    mollie.setApiKey(settings.MOLLIE_API_KEY)
    return mollie


def create_payment(request, registration):
    token = make_token(registration)

    redirect_url = request.build_absolute_uri(
            (reverse('status', args=[token])))

    p = {
        'amount': registration.amount_due,
        'description': 'Smokey Feet 2016',
        'redirectUrl': redirect_url,
        'metadata': {'registration_ref': registration.ref}
    }

    client = _make_mollie_client()

    try:
        payment = client.payments.create(p)
    except Mollie.API.Error as err:
        logger.error("Mollie API call failed: %s", err.message)
        raise
    else:
        assert 'id' in payment
        MolliePayment.objects.create(registration=registration,
                mollie_id=payment['id'], mollie_amount=registration.amount_due)

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
