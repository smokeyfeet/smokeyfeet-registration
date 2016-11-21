from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


def send_thanks_mail(registration):
    subject = "[SF2017] Signup received"

    context = {'registration': registration, 'subject': subject}
    text_msg = render_to_string('mail/thanks.text', context=context)
    html_msg = render_to_string('mail/thanks.html', context=context)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
            [registration.email], fail_silently=False,
            html_message=html_msg)


def send_completion_mail(registration):
    path = reverse('payment', args=[registration.id])
    url = "{}{}".format(settings.EMAIL_BASE_URI, path)
    subject = "[SF2017] Complete registration"

    context = {'registration': registration, 'subject': subject, 'url': url}
    text_msg = render_to_string('mail/complete.text', context=context)
    html_msg = render_to_string('mail/complete.html', context=context)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
           [registration.email], fail_silently=False,
           html_message=html_msg)


def send_payment_mail(registration):
    subject = "[SF2017] Payment received"
    context = {'registration': registration, 'subject': subject}

    text_msg = render_to_string('mail/payment.text', context=context)
    html_msg = render_to_string('mail/payment.html', context=context)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
            [registration.email], fail_silently=False,
            html_message=html_msg)


def send_payment_reminder_mail(registration):
    path = reverse('complete', args=[registration.id])
    url = "{}{}".format(settings.EMAIL_BASE_URI, path)
    subject = "[SF2017] Payment reminder"

    context = {'registration': registration, 'subject': subject, 'url': url}
    text_msg = render_to_string('mail/payment_reminder.text', context=context)
    html_msg = render_to_string('mail/payment_reminder.html', context=context)

    send_mail(subject, text_msg, settings.DEFAULT_FROM_EMAIL,
            [registration.email], fail_silently=False,
            html_message=html_msg)
