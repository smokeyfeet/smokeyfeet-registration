from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import (require_http_methods,
        require_POST, require_GET)

from . import mollie
from .forms import SignupForm, CompletionForm
from .models import Registration


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.save()
            return redirect('thanks')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


@require_GET
def thanks(request):
    return render(request, 'thanks.html')


@require_http_methods(["GET", "POST"])
def complete(request, ref):
    registration_id = ref
    registration = get_object_or_404(Registration.objects, pk=registration_id)

    if request.method == 'POST':
        form = CompletionForm(request.POST, instance=registration)
        if form.is_valid():
            questionare = form.save(commit=False)
            registration.save()
            mollie.make_payment(registration)
            return redirect('thanks')
    else:
        form = CompletionForm(instance=registration)

    return render(request, 'complete.html', {'form': form})


@require_http_methods(["GET", "POST"])
def done(request, ref):
    pass


@require_POST
def mollie_notif(request):
    """Mollie will notify us when a payment status
    changes. Only the payment id is passed and we
    are responsible for retieving the payment
    """
    # Pull out the payment id from the notification
    payment_id = request.POST.get("id", None)
    if payment_id is None:
        logger.error("Missing payment id in Mollie notification")
        return http.HttpResponseBadRequest()

    # Retrieve the payment
    try:
        payment = mollie.payments.get(payment_id)
    except Mollie.API.Error as e:
        logger.error("Mollie API call failed: %s", e.message)
        return http.HttpResponseServerError
    else:
        registration_ref = payment["metadata"]["registration_ref"]
        registration_id = hashids.decode(registration_ref)

        logger.info("Payment status for %d => %s", registration_id, status)

        if payment.isPaid():
            registration = Registration.objects.get(pk=registration_id)
            registration.mollie_status = "paid"
            registration.save()
