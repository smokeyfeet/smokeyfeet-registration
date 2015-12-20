from django.conf import settings
from django.core.urlresolvers import reverse

import Mollie


def _get_mollie_client():
    mollie = Mollie.API.Client()
    mollie.setApiKey(settings.MOLLIE_API_KEY)
    return mollie


def mollie_methods():
    try:
        methods = mollie.methods.all()
    except Mollie.API.Error as e:
        return 'API call failed: ' + e.message
    else:
        for method in methods:
            yield method


def make_payment(registration):
    p = {
        'amount': registration.amount_due,
        'description': 'Smokey Feet 2016 Registration',
        'webhookUrl':  reverse('mollie_notif'),
        #'redirectUrl': reverse('done', args=(registration.ref,)),
        'metadata': { 'registration_ref': registration.ref }
    }

    client = _get_mollie_client()

    try:
        payment = client.payments.create(p)
    except Mollie.API.Error as err:
        return "Mollie API call failed: {}".format(err.message)
    else:
        registration.mollie_status = payment['status']
        registration.save()
