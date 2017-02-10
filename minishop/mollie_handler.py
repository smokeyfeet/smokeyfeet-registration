import logging

from django.db import IntegrityError

from . import mailing
from .models import Order


logger = logging.getLogger(__name__)


def on_payment_change(mollie_payment):
    order_id = mollie_payment.get("metadata", {}).get("order_id", None)
    if order_id is None:
        logger.error("Mollie payment missing order_id")
        return

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning(
                "Order (%s) does not exist; Mollie status dropped", order_id)
        return

    if mollie_payment.isPaid():
        # Record the payment with the order
        try:
            order.payments.create(
                mollie_payment_id=mollie_payment["id"],
                amount=mollie_payment["amount"])
        except IntegrityError as err:
            logger.error("Order payment already exists: %s", str(err))

        if order.is_paid():
            mailing.send_order_paid_mail(order)

    elif (mollie_payment.isCancelled() or
            mollie_payment.isExpired() or
            mollie_payment.isFailed()):
        # HACK
        logger.info(
                "Payment unsuccessful; restock & delete order (%s) %s %s <%s>:",
                order.id, order.first_name, order.last_name, order.email)
        order.return_to_stock()
        order.delete()
