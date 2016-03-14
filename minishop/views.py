import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
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
    products = Product.objects.all()

    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            product = get_object_or_404(Product, pk=product_id)
            cart = Cart.objects.from_request(request)
            try:
                cart.add_to_cart(product)
            except MinishopException as err:
                messages.error(request, 'Failed to add to cart: %s' % str(err))
            else:
                return redirect('cart')

    return render(request, 'catalog.html', {'products': products})


@require_http_methods(["GET", "POST"])
def product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if form.is_valid():
            cart = Cart.objects.from_request(request)
            try:
                cart.add_to_cart(product)
            except MinishopException as err:
                messages.error(request, 'Failed to add to cart: %s' % str(err))
            else:
                return redirect('cart')
    else:
        form = AddProductForm(initial={'product_id': product.id})

    return render(request, 'product.html', {'product': product, 'form': form})


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
            'metadata': {'order_id': order.id}
            })
    except Mollie.API.Error as err:
        logger.error("Mollie API call failed: %s", err.message)
        raise
    else:
        return redirect(payment.getPaymentUrl())


@require_http_methods(["GET", "POST"])
def cart(request):
    cart = Cart.objects.from_request(request)

    if cart.is_empty:
        return render(request, 'cart_empty.html')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.amount = cart.amount_due
            order.save()
            _make_payment_then_redirect(request, order)
    else:
        form = OrderForm()

    return render(request, 'cart.html', {'cart': cart, 'form': form})
