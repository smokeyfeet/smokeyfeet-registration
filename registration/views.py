import logging

from django.conf import settings
from django.http import (HttpResponse, HttpResponseBadRequest,
        HttpResponseServerError)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (require_http_methods,
        require_POST, require_GET)
from hashids import Hashids
import jwt

from . import mailing
from . import mollie
from .forms import SignupForm, CompletionForm
from .models import Registration, MolliePayment


logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.save()
            mailing.send_thanks_mail(registration)
            mailing.send_completion_mail(registration)
            return redirect('thanks')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


@require_GET
def thanks(request):
    return render(request, 'thanks.html')


@require_http_methods(["GET", "POST"])
def complete(request, token):
    try:
        claims = jwt.decode(token, settings.SECRET_KEY)
    except jwt.InvalidTokenError as err:
        msg = "Invalid token: {}".format(type(err).__name__)
        return render(request, 'error.html', {'err': msg})
    else:
        registration_ref = claims.get('registration_ref', None)
        if registration_ref is not None:
            hashids = Hashids()
            registration_id, = hashids.decode(registration_ref)
        else:
            registration_id = None

    registration = get_object_or_404(Registration.objects, pk=registration_id)

    if request.method == 'POST':
        form = CompletionForm(request.POST, instance=registration)
        if form.is_valid():
            registration.save()
            payment = mollie.create_payment(request, registration)
            return redirect(payment.getPaymentUrl())
    else:
        form = CompletionForm(instance=registration)

    return render(request, 'complete.html', {'form': form})


@require_GET
def status(request, token):
    """
    Show the current registration status
    """
    try:
        claims = jwt.decode(token, settings.SECRET_KEY)
    except jwt.InvalidTokenError as err:
        msg = "Invalid token: {}".format(type(err).__name__)
        return render(request, 'error.html', {'err': msg})
    else:
        registration_ref = claims.get('registration_ref', None)
        if registration_ref is not None:
            hashids = Hashids()
            registration_id, = hashids.decode(registration_ref)
        else:
            registration_id = None

    registration = get_object_or_404(Registration.objects, pk=registration_id)

    return render(request, 'status.html', {'registration': registration})


@csrf_exempt
@require_POST
def mollie_notif(request):
    """Mollie will notify us when a payment status changes. Only
    the payment id is passed and we are responsible for retrieving
    the payment.
    """
    # Pull out the payment id from the notification
    payment_id = request.POST.get("id", None)
    if payment_id is None:
        logger.error("Missing payment id in Mollie notification")
        return HttpResponseBadRequest()

    # Retrieve the payment
    payment = mollie.retrieve_payment(payment_id)
    if payment is None:
        return HttpResponseServerError()
    else:
        registration_ref = payment["metadata"]["registration_ref"]
        hashids = Hashids()
        registration_id, = hashids.decode(registration_ref)

        logger.info("Payment (%s) status changed for registration %d => %s",
                payment_id, registration_id, payment['status'])

        try:
            mpay = MolliePayment.objects.get(mollie_id=payment_id)
        except MolliePayment.DoesNotExist:
            logger.warning("MolliePayment (%s) does not exist; status dropped",
                    payment_id)
        else:
            mpay.mollie_status = payment['status']
            mpay.save()

    return HttpResponse(status=201)
