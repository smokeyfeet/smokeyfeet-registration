from pathlib import Path
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET

from . import mailing
from . import mollie
from .forms import SignupForm
from .models import Registration


logger = logging.getLogger(__name__)


def signup_is_closed():
    return Path("/var/tmp/sf_closed").is_file()


@require_http_methods(["GET", "POST"])
def signup(request):

    if signup_is_closed():
        return render(request, "closed.html")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.fixate_price()
            registration.save()
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
            messages.error(request, "Could not create payment; try again later")

    return render(request, "status.html", {"registration": registration})


@login_required
def registrations(request):
    registrations = Registration.objects.all()
    return render(request, "list.html", {"registrations": registrations})


@login_required
def registration(request, registration_id):
    registration = get_object_or_404(Registration.objects, pk=registration_id)
    return render(request, "detail.html", {"registration": registration})
