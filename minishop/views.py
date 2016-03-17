import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import Mollie

from .exceptions import MinishopException
from .forms import AddProductForm, OrderForm
from .models import Cart, Order, Product


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order.html', {'order': order})


@require_http_methods(["GET", "POST"])
def catalog(request):
    products = Product.objects.in_stock()

    if not products.count():
        return render(request, 'catalog_soldout.html')

    if request.method == 'POST':
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
                return redirect('cart')

    return render(request, 'catalog.html', {'products': products})


def _make_payment_then_redirect(request, order):
    client = Mollie.API.Client()
    client.setApiKey(settings.MOLLIE_API_KEY)

    redirect_url = request.build_absolute_uri(
            (reverse('order', args=[order.id])))

    try:
        payment = client.payments.create({
            'amount': order.amount,
            'description': 'Smokey Feet 2016 PP',
            'redirectUrl': redirect_url,
            'metadata': {'order_id': str(order.id)}
            })
    except Mollie.API.Error as err:
        logger.error("Mollie API call failed: %s", err.message)
        raise
    else:
        return redirect(payment.getPaymentUrl())


@require_http_methods(["GET", "POST"])
@transaction.atomic
def cart(request):
    cart = Cart.objects.from_request(request)

    if cart.has_stockout_items():
        cart.remove_stockout_items()
        messages.warning(request, 'Out of stock items removed from cart')
        redirect('cart')

    if cart.is_empty:
        return render(request, 'cart_empty.html')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.add_items_from_cart(cart)
            _make_payment_then_redirect(request, order)
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
    client = Mollie.API.Client()
    client.setApiKey(settings.MOLLIE_API_KEY)

    try:
        payment = client.payments.get(payment_id)
    except Mollie.API.Error as err:
        logger.error("Mollie API call failed: %s", err.message)
        return HttpResponseServerError()

    order_id = payment.get("metadata", {}).get("order_id", None)
    logger.info("Payment (%s) status changed for order %s => %s",
                payment_id, str(order_id), payment['status'])

    if order_id is not None:
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            logger.warning(
                    "Order (%s) does not exist; status dropped", order_id)
        else:
            order.mollie_status = payment['status']
            order.save()

    return HttpResponse(status=200)
