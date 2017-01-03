from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import (
        Interaction, LunchType, PassType, Payment, Registration)
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
            return queryset.none()


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
            return queryset.exclude(
                    workshop_partner_email__exact=''
                ).exclude(workshop_partner_name__exact='')
        if self.value() == 'no':
            return queryset.filter(
                    workshop_partner_email__exact='',
                    workshop_partner_name__exact='')


class RegistrationAuditionFilter(admin.SimpleListFilter):
    title = _("has audition")

    parameter_name = "has_audition"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
            )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(audition_url__exact='')
        if self.value() == "no":
            return queryset.filter(audition_url__exact='')


def _workshop_partner(obj):
    return ("%s %s" % (obj.workshop_partner_name, obj.workshop_partner_email)).strip()


_workshop_partner.short_description = 'Workshop partner'


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1
    can_delete = False


class RegistrationAdmin(admin.ModelAdmin):
    list_filter = (RegistrationStatusFilter, 'pass_type', 'dance_role',
            RegistrationPartnerFilter, 'lunch', RegistrationAuditionFilter)

    list_display = ('first_name', 'last_name', 'email', 'pass_type',
            _workshop_partner, 'created_at', 'amount_paid')

    inlines = [PaymentInline, InteractionInline]

    ordering = ('created_at',)

    actions = [
            'action_accept',
            'action_payment_reminder',
            'action_cancel',
            'action_audition_received',
            'action_audition_reminder',
            'action_audition_accepted',
            ]

    def action_accept(self, request, queryset):
        for registration in queryset:

            if registration.accepted_at is None:
                registration.accepted_at = timezone.now()
                registration.save()

            mailing.send_registration_mail(
                    subject="[SF2017] Registration accepted",
                    template_name="mail/02_payment_instructions.html",
                    registration=registration)

    action_accept.short_description = "Accept and mail payment instructions"

    def action_payment_reminder(self, request, queryset):
        for registration in queryset:
            mailing.send_registration_mail(
                    subject="[SF2017] Payment reminder",
                    template_name="mail/03_payment_reminder.html",
                    registration=registration)

    action_payment_reminder.short_description = "Mail payment reminder"

    def action_cancel(self, request, queryset):
        for registration in queryset:
            mailing.send_registration_mail(
                    subject="[SF2017] Registration cancelled",
                    template_name="mail/05_cancel.html",
                    registration=registration)

    action_cancel.short_description = "Mail cancel notification"

    def action_audition_received(self, request, queryset):
        for registration in queryset:
            mailing.send_registration_mail(
                    subject="[SF2017] Video audition received",
                    template_name="mail/06a_audition_received.html",
                    registration=registration)

    action_audition_received.short_description = "Mail audition received notification"

    def action_audition_reminder(self, request, queryset):
        for registration in queryset:
            mailing.send_registration_mail(
                    subject="[SF2017] Video audition reminder",
                    template_name="mail/09_audition_reminder.html",
                    registration=registration)

    action_audition_reminder.short_description = "Mail audition reminder"

    def action_audition_accepted(self, request, queryset):
        for registration in queryset:
            mailing.send_registration_mail(
                    subject="[SF2017] Video audition accepted",
                    template_name="mail/06b_audition_accepted.html",
                    registration=registration)

    action_audition_accepted.short_description = "Mail audition accepted notification"


admin.site.register(LunchType, LunchTypeAdmin)
admin.site.register(PassType, PassTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
