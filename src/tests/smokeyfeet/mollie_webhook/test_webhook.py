from django.urls import reverse
import pytest

from mollie.api.error import Error as MollieError
from mollie.api.objects.payment import Payment as MolliePayment


URL = reverse("mollie_webhook:mollie_notif")


def test_missing_id(client):
    response = client.post(URL, data={})
    assert response.status_code == 200


def test_missing_payment(client, mocker):
    mocker.patch(
        "mollie.api.resources.payments.Payments.get",
        autospec=True,
        return_value=None,
        side_effect=MollieError(),
    )

    response = client.post(URL, data={"id": "XXX"})
    # mock.assert_called_once_with("XXX")

    assert response.status_code == 500


def test_missing_meta_registration_id(client, mocker):
    mocker.patch(
        "mollie.api.resources.payments.Payments.get",
        autospec=True,
        return_value=dict(status="paid", metadata={}),
    )

    response = client.post(URL, data={"id": "XXX"})
    # mock.assert_called_once_with("XXX")
    assert response.status_code == 200


@pytest.mark.django_db
def test_paid(client, mocker, registration):
    mollie_payment_id = "tr_XXX"

    mocker.patch(
        "mollie.api.resources.payments.Payments.get",
        autospec=True,
        return_value=MolliePayment(
            {
                "id": mollie_payment_id,
                "metadata": {"registration_id": registration.id},
                "status": MolliePayment.STATUS_PAID,
                "paidAt": "2018-03-20T13:28:37+00:00",
                "amount": {"currency": "EUR", "value": "100.0"},
            }
        ),
    )
    response = client.post(URL, data={"id": mollie_payment_id})

    # mock.assert_called_once_with(mollie_payment_id)
    assert response.status_code == 200

    payment = registration.payment_set.first()
    assert payment is not None

    assert payment.mollie_payment_id == mollie_payment_id
    assert payment.amount == 100.0


@pytest.mark.django_db
def test_cancelled(client, mocker, registration):
    mollie_payment_id = "tr_XXX"

    mocker.patch(
        "mollie.api.resources.payments.Payments.get",
        autospec=True,
        return_value=MolliePayment(
            {
                "id": mollie_payment_id,
                "metadata": {"registration_id": registration.id},
                "status": MolliePayment.STATUS_CANCELED,
            }
        ),
    )
    response = client.post(URL, data={"id": mollie_payment_id})
    # mock.assert_called_once_with(mollie_payment_id)
    assert response.status_code == 200
