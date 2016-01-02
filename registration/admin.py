from django.contrib import admin

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

    actions = ['action_complete']

    def action_complete(self, request, queryset):
        for registration in queryset:
            mailing.send_completion_mail(registration)

    action_complete.short_description = "Accept and send completion mail"


admin.site.register(PassType, PassTypeAdmin)
admin.site.register(CompetitionType, CompetitionTypeAdmin)
admin.site.register(VolunteerType, VolunteerTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
