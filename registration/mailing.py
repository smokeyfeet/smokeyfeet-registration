from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from html2text import html2text


def send_registration_mail(subject, template_name, registration):
    status_url = urljoin(
            settings.EMAIL_BASE_URI,
            reverse("registration:status", args=[registration.id]))

    context = dict(
        subject=subject,
        registration=registration,
        status_url=status_url)

    html_msg = render_to_string(template_name, context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)

    registration.log_interaction(
            "Mailed {} with subject: {}".format(registration.email, subject))


def send_signup_received(registration):
    subject = "[SF2017] Signup received"
    context = dict(registration=registration)

    html_msg = render_to_string(
            "mail/01_auto_signup.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)

    registration.log_interaction(
            "Mailed {} with subject: {}".format(registration.email, subject))


def send_payment_received(registration):
    subject = "[SF2017] Payment received"
    context = dict(registration=registration)

    html_msg = render_to_string(
            "mail/04_auto_payment_received.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)

    registration.log_interaction(
            "Mailed {} with subject: {}".format(registration.email, subject))
