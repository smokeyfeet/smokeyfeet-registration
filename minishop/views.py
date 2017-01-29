import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from Mollie.API import Payment

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

    # Hack; canceling payment results in deleting the order
    if order.mollie_payment_status == Payment.STATUS_CANCELLED:
        logger.info(
                "Payment canceled; restock & delete order (%s) %s %s <%s>:",
                order.id, order.first_name, order.last_name, order.email)

        order.return_to_stock()
        order.delete()
        return redirect('minishop:catalog')

    return render(request, 'order.html', {'order': order})


@require_http_methods(["GET", "POST"])
def catalog(request):
    products = Product.objects.all()

    if request.method == 'POST' and 'add_to_cart' in request.POST:
        form = AddProductForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            product = get_object_or_404(Product, pk=product_id)
            cart = Cart.objects.from_request(request)
            try:
                cart.add_product(product)
            except MinishopException as err:
                messages.error(request, 'Failed to add to cart: %s' % str(err))
            else:
                return redirect('minishop:cart')

    return render(request, 'catalog.html', {'products': products})


@require_http_methods(["GET", "POST"])
@transaction.atomic
def cart(request):
    cart = Cart.objects.from_request(request)

    if request.method == 'POST' and 'remove_item' in request.POST:
        item_id = request.POST.get('item_id', None)
        if item_id is not None:
            cart.remove_item_by_id(item_id)

    if cart.is_empty:
        return render(request, 'cart_empty.html')

    if request.method == 'POST' and 'backorder' in request.POST:
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.status = Order.STATUS_BACKORDER
            order.save()

            order.add_items_from_cart(cart, verify_stock=False)

            cart.clear()  # clear out cart on successful order; perhaps delete

            return redirect('minishop:catalog')

    elif request.method == 'POST' and 'pay' in request.POST:
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.add_items_from_cart(cart)

            cart.clear()  # clear out cart on successful order; perhaps delete

            payment = mollie.create_payment(request, order)
            if payment is not None:

                # Associate Mollie payment with order
                order.mollie_payment_id = payment['id']
                order.mollie_payment_status = payment['status']
                order.save()

                return redirect(payment.getPaymentUrl())
            else:
                messages.error(
                    request, "Could not create payment; try again later")
    else:
        form = OrderForm()

    return render(request, 'cart.html', {'cart': cart, 'form': form})


@csrf_exempt
@require_http_methods(["POST"])
def mollie_notif(request):
    """Mollie will notify us when a payment status changes. Only
    the payment id is passed and we are responsible for retrieving
    the payment.
    """
    # Pull out the payment id from the notification
    payment_id = request.POST.get("id", "")
    if not payment_id:
        logger.warning("Missing payment id in Mollie notif (probably test)")
        return HttpResponse(status=200)

    # Retrieve the payment
    payment = mollie.retrieve_payment(payment_id)
    if payment is None:
        return HttpResponseServerError()

    order_id = payment.get("metadata", {}).get("order_id", None)
    logger.info("Payment (%s) status changed for order %s => %s",
                payment_id, str(order_id), payment['status'])

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning(
                "Order (%s) does not exist; Mollie status dropped", order_id)
    else:
        if payment.isPaid():
            order.status = Order.STATUS_PAID
            order.mollie_payment_status = payment['status']
            order.save()

            send_order_paid_mail(order)

    return HttpResponse(status=200)
