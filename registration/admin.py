from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import LunchType, PassType, Registration
from . import mailing


class LunchTypeAdmin(admin.ModelAdmin):
    pass


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
            )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(accepted_at__isnull=True)
        if self.value() == 'accepted':
            return queryset.filter(accepted_at__isnull=False)
        if self.value() == 'paid':
            return queryset.filter(payment_status="paid")


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
            RegistrationPartnerFilter, 'lunch')

    list_display = ('first_name', 'last_name', 'email', 'pass_type',
            _workshop_partner, 'created_at')

    ordering = ('created_at',)

    actions = ['action_complete', 'action_payment_reminder']

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


admin.site.register(LunchType, LunchTypeAdmin)
admin.site.register(PassType, PassTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
