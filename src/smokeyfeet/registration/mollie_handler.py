import logging

from . import mailing
from .models import Registration


logger = logging.getLogger(__name__)


def on_payment_change(mollie_payment):
    registration_id = mollie_payment.metadata.get("registration_id", None)
    if registration_id is None:
        logger.error("Mollie payment missing registration_id")
        return

    try:
        registration = Registration.objects.get(pk=registration_id)
    except Registration.DoesNotExist:
        logger.warning(
            "Registration (%s) does not exist; Mollie status dropped", registration_id
        )
    else:
        if mollie_payment.is_paid():
            registration.payment_set.create(
                mollie_payment_id=mollie_payment.id,
                amount=mollie_payment.amount["value"],
            )
            mailing.send_payment_received(registration)
