import datetime as dt

from Mollie.API import Payment
from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import PassType, Registration
from . import mailing


class PassTypeAdmin(admin.ModelAdmin):
    pass


class RegistrationStatusFilter(admin.SimpleListFilter):
    title = _('status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('pending', _('Signup pending')),
            ('accepted', _('Signup accepted')),
            ('paid', _('Paid')),
            ('accepted_unpaid_07d', _('Accepted & unpaid 7d')),
            ('accepted_unpaid_10d', _('Accepted & unpaid 10d')),
            ('accepted_unpaid_14d', _('Accepted & unpaid 14d')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(accepted_at__isnull=True)
        #if self.value() == 'accepted':
        #    return queryset.filter(accepted_at__isnull=False)
        #if self.value() == 'paid':
            #reg_ids = MolliePayment.objects.filter(
            #        mollie_status=Payment.STATUS_PAID).values_list('registration_id',
            #                flat=True)
            #return queryset.filter(pk__in=set(reg_ids))
        #if self.value() == 'accepted_unpaid_07d':
        #    return queryset.filter(accepted_at__lte=timezone.now() -
        #            dt.timedelta(days=7)).exclude(molliepayment__mollie_status=Payment.STATUS_PAID)
        #if self.value() == 'accepted_unpaid_10d':
        #    return queryset.filter(accepted_at__lte=timezone.now() -
        #            dt.timedelta(days=10)).exclude(molliepayment__mollie_status=Payment.STATUS_PAID)
        #if self.value() == 'accepted_unpaid_14d':
        #    return queryset.filter(accepted_at__lte=timezone.now() -
        #            dt.timedelta(days=14)).exclude(molliepayment__mollie_status=Payment.STATUS_PAID)


class RegistrationPartnerFilter(admin.SimpleListFilter):
    title = _('has partner')

    parameter_name = 'has_partner'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(workshop_partner_email__exact=''
                    ).exclude(workshop_partner_name__exact='')
        if self.value() == 'no':
            return queryset.filter(workshop_partner_email__exact='',
                    workshop_partner_name__exact='')


def _workshop_partner(obj):
    return ("%s %s" % (obj.workshop_partner_name, obj.workshop_partner_email)).strip()
_workshop_partner.short_description = 'Workshop partner'


class RegistrationAdmin(admin.ModelAdmin):
    list_filter = (RegistrationStatusFilter, 'pass_type', 'dance_role',
            RegistrationPartnerFilter, 'include_lunch')

    list_display = ('first_name', 'last_name', 'email', 'pass_type',
            _workshop_partner, 'created_at')

    ordering = ('created_at',)

    actions = ['action_complete', 'action_payment_reminder']

    #inlines = [MolliePaymentInline]

    def action_complete(self, request, queryset):
        for registration in queryset:
            registration.accepted_at = timezone.now()
            registration.save()
            mailing.send_completion_mail(registration)

    action_complete.short_description = "Accept and send completion mail"

    def action_payment_reminder(self, request, queryset):
        for registration in queryset:
            registration.payment_reminder_at = timezone.now()
            registration.save()
            mailing.send_payment_reminder_mail(registration)

    action_payment_reminder.short_description = "Send payment reminder mail"


admin.site.register(PassType, PassTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
