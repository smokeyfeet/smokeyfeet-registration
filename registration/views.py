import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (require_http_methods,
        require_POST, require_GET)

from . import mailing
from . import mollie
from .forms import SignupForm
from .models import Registration


logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            registration = form.save()
            mailing.send_signup_received(registration)
            return redirect("registration:thanks")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


@require_GET
def thanks(request):
    return render(request, "thanks.html")


@require_http_methods(["GET", "POST"])
def status(request, registration_id):

    registration = get_object_or_404(Registration.objects, pk=registration_id)

    if request.method == "POST" and "make_payment" in request.POST:
        payment = mollie.create_payment(request, registration)
        if payment is not None:
            return redirect(payment.getPaymentUrl())
        else:
            messages.error(
                    request, "Could not create payment; try again later")

    return render(request, "status.html", {"registration": registration})


@csrf_exempt
@require_POST
def mollie_notif(request):
    """
    Mollie will notify us when a payment status changes. Only the payment id is
    passed and we are responsible for retrieving the payment.
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
    else:
        registration_id = payment.get("metadata", {}).get("registration_id", None)
        if registration_id is not None:
            logger.info(
                    "Mollie payment (%s) status changed for registration %d => %s",
                    payment_id, registration_id, payment["status"])
        else:
            logger.info(
                    "Mollie payment (%s) status changed => %s",
                    payment_id, payment["status"])

        try:
            registration = Registration.objects.get(pk=registration_id)
        except Registration.DoesNotExist:
            logger.warning(
                    "Registration (%s) does not exist; Mollie status dropped",
                    payment_id)
        else:
            # Update status
            registration.payment_status = payment["status"]
            registration.payment_status_at = timezone.now()
            registration.save()

            if payment.isPaid():
                mailing.send_payment_received(registration)

    return HttpResponse(status=200)


@login_required
def registrations(request):
    registrations = Registration.objects.all()
    return render(
            request, "list.html", {"registrations": registrations})


@login_required
def registration(request, registration_id):
    registration = get_object_or_404(Registration.objects, pk=registration_id)
    return render(request, "detail.html", {"registration": registration})
