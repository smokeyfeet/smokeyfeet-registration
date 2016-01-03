from django.contrib import admin
from django.utils import timezone

from .models import PassType, CompetitionType, VolunteerType, Registration
from . import mailing


class PassTypeAdmin(admin.ModelAdmin):
    pass


class CompetitionTypeAdmin(admin.ModelAdmin):
    pass


class VolunteerTypeAdmin(admin.ModelAdmin):
    pass


class RegistrationAdmin(admin.ModelAdmin):
    list_filter = ('pass_type',)
    list_display = ('first_name', 'last_name', 'pass_type', 'created_at')

    ordering = ('created_at',)

    actions = ['action_complete']

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
