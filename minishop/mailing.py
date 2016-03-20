from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_order_mail(order):
    subject = "[SF2016] Order"

    context = {'order': order, 'subject': subject}
    text_msg = render_to_string('mail/order.text', context=context)
    html_msg = render_to_string('mail/order.html', context=context)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
            [order.email], fail_silently=False,
            html_message=html_msg)
