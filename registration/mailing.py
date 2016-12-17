from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from html2text import html2text


def send_thanks_mail(registration):
    subject = "[SF2017] Signup received"

    context = {"registration": registration, "subject": subject}
    html_msg = render_to_string("mail/thanks.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)


def send_completion_mail(registration):
    path = reverse("registration:status", args=[registration.id])
    url = "{}{}".format(settings.EMAIL_BASE_URI, path)
    subject = "[SF2017] Complete registration"

    context = {"registration": registration, "subject": subject, "url": url}
    html_msg = render_to_string("mail/complete.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)


def send_payment_mail(registration):
    subject = "[SF2017] Payment received"
    context = {"registration": registration, "subject": subject}

    html_msg = render_to_string("mail/payment.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)


def send_payment_reminder_mail(registration):
    path = reverse("registration:status", args=[registration.id])
    url = "{}{}".format(settings.EMAIL_BASE_URI, path)
    subject = "[SF2017] Payment reminder"

    context = {"registration": registration, "subject": subject, "url": url}
    html_msg = render_to_string("mail/payment_reminder.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [registration.email], fail_silently=False,
              html_message=html_msg)
