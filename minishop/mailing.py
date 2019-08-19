from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from html2text import html2text


def send_order_paid_mail(order):
    subject = "[SF2017] Order"

    path = reverse("minishop:order", args=[order.id])
    order_url = urljoin(settings.EMAIL_BASE_URI, path)
    context = {"order": order, "subject": subject, "order_url": order_url}
    html_msg = render_to_string("mail/order_paid.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [order.email], fail_silently=False,
              html_message=html_msg)


def send_backorder_mail(order):
    subject = "[SF2017] Waiting list"

    path = reverse("minishop:order", args=[order.id])
    order_url = urljoin(settings.EMAIL_BASE_URI, path)
    context = {"order": order, "subject": subject, "order_url": order_url}
    html_msg = render_to_string("mail/order_backorder.html", context=context)
    text_msg = html2text(html_msg)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
              [order.email], fail_silently=False,
              html_message=html_msg)
