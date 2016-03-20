from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


def send_order_paid_mail(order):
    subject = "[SF2016] Order"

    path = reverse('order', args=[order.id])
    order_url = "{}{}".format(settings.EMAIL_BASE_URI, path)
    context = {'order': order, 'subject': subject, 'order_url': order_url}
    text_msg = render_to_string('mail/order_paid.text', context=context)
    html_msg = render_to_string('mail/order_paid.html', context=context)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
            [order.email], fail_silently=False,
            html_message=html_msg)
