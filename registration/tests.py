from unittest import mock

from django.test import Client as HttpClient, TestCase
from django.urls import reverse
import Mollie.API.Error
from Mollie.API.Object.Payment import Payment as MolliePayment

from .models import Registration, PassType, LunchType


class SignupTestCase(TestCase):

    def setUp(self):
        self.client = HttpClient()
        self.path = reverse("registration:signup")

    def test_signup_get(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_signup_post(self):
        response = self.client.post(self.path, data={})
        self.assertEqual(response.status_code, 200)


class ThanksTestCase(TestCase):

    def setUp(self):
        self.client = HttpClient()
        self.path = reverse("registration:thanks")

    def test_thanks(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)


class StatusTestCase(TestCase):

    fixtures = ["lunch_types.json", "pass_types.json"]

    @classmethod
    def setUpTestData(cls):
        lunch = LunchType.objects.first()
        pass_type = PassType.objects.first()
        cls.registration = Registration.objects.create(
                lunch=lunch, pass_type=pass_type)

    def setUp(self):
        self.client = HttpClient()

    def test_status_get(self):
        path = reverse("registration:status", args=[self.registration.id])
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    @mock.patch("Mollie.API.Resource.Payments.create")
    def test_status_post_success(self, mock_create):
        mollie_payment_id = "tr_XXX"
        mock_create.return_value = MolliePayment(
                id=mollie_payment_id,
                metadata={"registration_id": self.registration.id},
                status="cancelled",
                links={"paymentUrl": "https://x/{}".format(mollie_payment_id)}
                )
        path = reverse("registration:status", args=[self.registration.id])
        response = self.client.post(path, data={"make_payment": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://x/tr_XXX")

    @mock.patch("Mollie.API.Resource.Payments.create")
    def test_status_post_fail(self, mock_create):
        mollie_payment_id = "tr_XXX"
        mock_create.return_value = None
        path = reverse("registration:status", args=[self.registration.id])
        response = self.client.post(path, data={"make_payment": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(u"Could not create payment", str(response.content))


class MollieNotifTestCase(TestCase):

    fixtures = ["lunch_types.json", "pass_types.json"]

    @classmethod
    def setUpTestData(cls):
        lunch = LunchType.objects.first()
        pass_type = PassType.objects.first()
        cls.registration = Registration.objects.create(
                lunch=lunch, pass_type=pass_type)

    def setUp(self):
        self.client = HttpClient()
        self.path = reverse("registration:mollie_notif")

    def test_missing_id(self):
        response = self.client.post(self.path, data={})
        self.assertEqual(response.status_code, 200)

    @mock.patch("Mollie.API.Resource.Payments.get")
    def test_missing_payment(self, mock_get):
        mock_get.side_effect = Mollie.API.Error()
        mock_get.return_value = None
        response = self.client.post(self.path, data={"id": "XXX"})
        mock_get.assert_called_once_with("XXX")
        self.assertEqual(response.status_code, 500)

    @mock.patch("Mollie.API.Resource.Payments.get")
    def test_missing_meta_registration_id(self, mock_get):
        mock_get.return_value = dict(status="paid", metadata={})
        response = self.client.post(self.path, data={"id": "XXX"})
        mock_get.assert_called_once_with("XXX")
        self.assertEqual(response.status_code, 200)

    @mock.patch("Mollie.API.Resource.Payments.get")
    def test_paid(self, mock_get):
        mollie_payment_id = "tr_XXX"
        mock_get.return_value = MolliePayment(
                id=mollie_payment_id,
                metadata={"registration_id": self.registration.id},
                status="paid",
                paidDatetime="foo",
                amount=100.0,
                )
        response = self.client.post(self.path, data={"id": mollie_payment_id})
        mock_get.assert_called_once_with(mollie_payment_id)
        self.assertEqual(response.status_code, 200)
        payment = self.registration.payment_set.first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.mollie_payment_id, mollie_payment_id)
        self.assertEqual(payment.amount, 100.0)

    @mock.patch("Mollie.API.Resource.Payments.get")
    def test_cancelled(self, mock_get):
        mollie_payment_id = "tr_XXX"
        mock_get.return_value = MolliePayment(
                id=mollie_payment_id,
                metadata={"registration_id": self.registration.id},
                status="cancelled",
                )
        response = self.client.post(self.path, data={"id": mollie_payment_id})
        mock_get.assert_called_once_with(mollie_payment_id)
        self.assertEqual(response.status_code, 200)
