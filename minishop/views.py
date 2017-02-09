import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import mollie
from .exceptions import MinishopException
from .forms import AddProductForm, OrderForm
from .mailing import send_order_paid_mail
from .models import Cart, Order, Product


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@transaction.atomic
def order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "order.html", {"order": order})


@require_http_methods(["GET", "POST"])
def catalog(request):
    products = Product.objects.all()

    if request.method == "POST" and "add_to_cart" in request.POST:
        form = AddProductForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data["product_id"]
            product = get_object_or_404(Product, pk=product_id)
            cart = Cart.objects.from_request(request)

            try:
                cart.add_product(product)
            except MinishopException as err:
                msg = "Could not add product to cart: {}".format(err)
                messages.error(request, msg)
            else:
                return redirect("minishop:cart")

    return render(request, "catalog.html", {"products": products})


@require_http_methods(["GET", "POST"])
@transaction.atomic
def cart(request):
    cart = Cart.objects.from_request(request)

    if request.method == "POST" and "remove_item" in request.POST:
        item_id = request.POST.get("item_id", None)
        if item_id is not None:
            cart.remove_item_by_id(item_id)

    if cart.is_empty():
        return render(request, "cart_empty.html")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.add_items_from_cart(cart)

            cart.clear()  # clear out cart on successful order; perhaps delete

            if order.has_backorder_items():
                return redirect("minishop:order", order_id=order.id)
            else:
                payment = mollie.create_payment(request, order)
                if payment is not None:
                    return redirect(payment.getPaymentUrl())
                else:
                    messages.error(
                        request, "Could not create payment; try again later")
    else:
        form = OrderForm()

    return render(request, "cart.html", {"cart": cart, "form": form})


@csrf_exempt
@require_http_methods(["POST"])
def mollie_notif(request):
    """Mollie will notify us when a payment status changes. Only
    the payment id is passed and we are responsible for retrieving
    the payment.
    """
    # Pull out the Mollie payment id from the notification
    mollie_payment_id = request.POST.get("id", "")
    if not mollie_payment_id:
        logger.warning("Missing payment id in Mollie notif (probably test)")
        return HttpResponse(status=200)

    # Retrieve the Mollie payment
    mollie_payment = mollie.retrieve_payment(mollie_payment_id)
    if mollie_payment is None:
        return HttpResponseServerError()

    order_id = mollie_payment.get("metadata", {}).get("order_id", None)
    logger.info("Payment (%s) status changed for order %s => %s",
                mollie_payment_id, str(order_id), mollie_payment["status"])

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning(
                "Order (%s) does not exist; Mollie status dropped", order_id)

    if mollie_payment.isPaid():
        # Record the payment with the order
        order.payments.create(
            mollie_payment_id=mollie_payment["id"],
            amount=mollie_payment["amount"])

        if order.is_paid_in_full():
            send_order_paid_mail(order)

    elif (mollie_payment.isCancelled() or
            mollie_payment.isExpired() or
            mollie_payment.isFailed()):
        # HACK
        logger.info(
                "Payment unsuccessful; restock & delete order (%s) %s %s <%s>:",
                order.id, order.first_name, order.last_name, order.email)
        order.return_to_stock()
        order.delete()

    return HttpResponse(status=200)
