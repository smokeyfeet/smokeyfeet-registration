from pathlib import Path
import logging

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from . import mailing
from . import mollie
from .exceptions import MinishopException
from .forms import AddProductForm, OrderForm
from .models import Cart, Order, Product


logger = logging.getLogger(__name__)


def shop_is_closed():
    return Path("/var/tmp/sf_shop_closed").is_file()


@require_http_methods(["GET", "POST"])
def catalog(request):

    if shop_is_closed():
        return render(request, "closed.html")

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
                mailing.send_backorder_mail(order)

            return redirect("minishop:order", order_id=order.id)
    else:
        form = OrderForm()

    return render(request, "cart.html", {"cart": cart, "form": form})


@require_http_methods(["GET", "POST"])
@transaction.atomic
def order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == "POST" and "make_payment" in request.POST:
        payment = mollie.create_payment(request, order)
        if payment is not None:
            return redirect(payment.getPaymentUrl())
        else:
            messages.error(
                    request, "Could not create payment; try again later")
    return render(request, "order.html", {"order": order})
