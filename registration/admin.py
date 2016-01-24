import datetime as dt

from Mollie.API import Payment
from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import (PassType, CompetitionType, MolliePayment,
        VolunteerType, Registration)
from . import mailing
from .utils import make_token


class PassTypeAdmin(admin.ModelAdmin):
    pass


class CompetitionTypeAdmin(admin.ModelAdmin):
    pass


class VolunteerTypeAdmin(admin.ModelAdmin):
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
        if self.value() == 'accepted':
            return queryset.filter(accepted_at__isnull=False)
        if self.value() == 'paid':
            return queryset.filter(molliepayment__mollie_status=Payment.STATUS_PAID)
        if self.value() == 'accepted_unpaid_07d':
            return queryset.filter(accepted_at__lte=timezone.now() -
                    dt.timedelta(days=7)).exclude(molliepayment__mollie_status=Payment.STATUS_PAID)
        if self.value() == 'accepted_unpaid_10d':
            return queryset.filter(accepted_at__lte=timezone.now() -
                    dt.timedelta(days=10)).exclude(molliepayment__mollie_status=Payment.STATUS_PAID)
        if self.value() == 'accepted_unpaid_14d':
            return queryset.filter(accepted_at__lte=timezone.now() -
                    dt.timedelta(days=14)).exclude(molliepayment__mollie_status=Payment.STATUS_PAID)


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


class MolliePaymentInline(admin.TabularInline):
    model = MolliePayment
    extra = 0
    #readonly_fields = ('mollie_id', 'mollie_amount', 'mollie_status',
    #        'created_at')
    exclude = ('updated_at',)


def _workshop_partner(obj):
    return ("%s %s" % (obj.workshop_partner_name, obj.workshop_partner_email)).strip()
_workshop_partner.short_description = 'Workshop partner'


class RegistrationForm(forms.ModelForm):
    token = forms.CharField(label='Token', required=False)

    class Meta:
        model = Registration
        exclude = []


class RegistrationAdmin(admin.ModelAdmin):
    form = RegistrationForm

    list_filter = (RegistrationStatusFilter, 'pass_type', 'dance_role',
            RegistrationPartnerFilter, 'include_lunch')

    list_display = ('first_name', 'last_name', 'email', 'pass_type',
            _workshop_partner, 'amount_paid', 'created_at')

    ordering = ('created_at',)

    actions = ['action_complete', 'action_payment_reminder']

    inlines = [MolliePaymentInline]

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

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegistrationAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.base_fields['token'].initial = make_token(obj)
        return form


admin.site.register(PassType, PassTypeAdmin)
admin.site.register(CompetitionType, CompetitionTypeAdmin)
admin.site.register(VolunteerType, VolunteerTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
