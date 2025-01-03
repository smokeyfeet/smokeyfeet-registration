import logging

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mollie.api.client import Client as MollieClient
from mollie.api.error import Error as MollieError

from smokeyfeet.minishop import mollie_handler as minishop_mollie
from smokeyfeet.registration import mollie_handler as registration_mollie

logger = logging.getLogger(__name__)


def _make_mollie_client():
    mollie_client = MollieClient()
    mollie_client.set_api_key(settings.MOLLIE_API_KEY)
    return mollie_client


def retrieve_payment(payment_id):
    mollie_client = _make_mollie_client()

    try:
        payment = mollie_client.payments.get(payment_id)
    except MollieError as err:
        logger.error("Mollie API call failed: %s", str(err))
        return None
    else:
        return payment


@csrf_exempt
@require_POST
def mollie_notif(request):
    """
    Mollie will notify us when a payment status changes. Only the payment id is
    passed and we are responsible for retrieving the payment.
    """
    # Pull out the Mollie payment id from the notification
    mollie_payment_id = request.POST.get("id", "")
    if not mollie_payment_id:
        logger.warning("Missing payment id in Mollie notif (probably test)")
        return HttpResponse(status=200)

    logger.info("Got Mollie payment status update: %s", mollie_payment_id)

    # Retrieve the Mollie payment
    mollie_payment = retrieve_payment(mollie_payment_id)
    if mollie_payment is None:
        logger.error("Failed to retrieve Mollie payment: %s", mollie_payment_id)
        return HttpResponseServerError()
    else:
        logger.info("Retrieved Mollie payment: %s", str(mollie_payment))

    metadata = mollie_payment.get("metadata", {})
    if "order_id" in metadata:
        minishop_mollie.on_payment_change(mollie_payment)
    elif "registration_id" in metadata:
        registration_mollie.on_payment_change(mollie_payment)
    else:
        logger.error("Missing identifier in Mollie payment: %s", str(mollie_payment))

    return HttpResponse(status=200)
