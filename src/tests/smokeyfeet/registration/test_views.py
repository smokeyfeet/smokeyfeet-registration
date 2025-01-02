import pytest
from django.urls import reverse
from mollie.api.objects.payment import Payment as MolliePayment


@pytest.mark.django_db
def test_signup(client):
    url = reverse("registration:signup")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_thanks(client):
    url = reverse("registration:thanks")

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["registration:signup"])
def test_public_views(view_name, client):
    """
    Ensure views not requiring authentication are accessible
    """
    response = client.get(reverse(view_name))
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup_post(client):
    url = reverse("registration:signup")
    response = client.post(url, data={})
    assert response.status_code == 200


@pytest.mark.django_db
def test_status_get(client, registration):
    url = reverse("registration:status", args=[registration.id])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_status_post_success(client, registration, mocker):
    mollie_payment_id = "tr_XXX"

    mocker.patch(
        "mollie.api.resources.payments.Payments.create",
        autospec=True,
        return_value=MolliePayment(
            data={
                "id": mollie_payment_id,
                "metadata": {"registration_id": registration.id},
                "status": MolliePayment.STATUS_CANCELED,
                "_links": {"checkout": {"href": f"https://x/{mollie_payment_id}"}},
            },
            client=None,
        ),
    )

    url = reverse("registration:status", args=[registration.id])
    response = client.post(url, data={"make_payment": ""})
    assert response.status_code == 302
    assert response.url == "https://x/tr_XXX"


@pytest.mark.django_db
def test_status_post_fail(client, registration, mocker):
    mocker.patch(
        "mollie.api.resources.payments.Payments.create",
        autospec=True,
        return_value=None,
    )
    url = reverse("registration:status", args=[registration.id])
    response = client.post(url, data={"make_payment": ""})
    assert response.status_code == 200
    assert "Could not create payment" in str(response.content)


@pytest.mark.django_db
def test_registrations(authenticated_user, client, registration):
    url = reverse("registration:list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_registration(authenticated_user, client, registration):
    url = reverse("registration:detail", args=[registration.id])
    response = client.get(url)
    assert response.status_code == 200
