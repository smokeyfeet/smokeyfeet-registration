from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import (PassType, CompetitionType, MolliePayment,
        VolunteerType, Registration)
from . import mailing


class PassTypeAdmin(admin.ModelAdmin):
    pass


class CompetitionTypeAdmin(admin.ModelAdmin):
    pass


class VolunteerTypeAdmin(admin.ModelAdmin):
    pass


class RegistrationStatusFilter(admin.SimpleListFilter):
    title = _('status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('pending', _('Signup pending')),
            ('accepted', _('Signup accepted')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(accepted_at__isnull=True)
        if self.value() == 'accepted':
            return queryset.filter(accepted_at__isnull=False)


class MolliePaymentInline(admin.TabularInline):
    model = MolliePayment
    extra = 0
    readonly_fields = ('mollie_id', 'mollie_status', 'created_at')
    exclude = ('updated_at',)


class RegistrationAdmin(admin.ModelAdmin):
    list_filter = (RegistrationStatusFilter, 'pass_type', 'dance_role')
    list_display = ('first_name', 'last_name', 'pass_type', 'created_at')

    ordering = ('created_at',)

    actions = ['action_complete']

    inlines = [MolliePaymentInline]

    def action_complete(self, request, queryset):
        for registration in queryset:
            registration.accepted_at = timezone.now()
            registration.save()
            mailing.send_completion_mail(registration)

    action_complete.short_description = "Accept and send completion mail"


admin.site.register(PassType, PassTypeAdmin)
admin.site.register(CompetitionType, CompetitionTypeAdmin)
admin.site.register(VolunteerType, VolunteerTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
