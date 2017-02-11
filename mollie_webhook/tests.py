from unittest import mock
from django.test import TestCase, Client as HttpClient
from django.urls import reverse


class TestMollieNotif(TestCase):

    def setUp(self):
        self.client = HttpClient()
        self.path = reverse("mollie_webhook:mollie_notif")

    @mock.patch("Mollie.API.Resource.Payments.get")
    def test_x(self, get_func):
        get_func.side_effect = Exception("Boom!")
        # Mollie.API.Error
        self.client.post(self.path, {"payment_id": "tr_XXX"})
