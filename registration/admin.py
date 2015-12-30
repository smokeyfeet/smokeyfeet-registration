from django.contrib import admin

from .models import PassType, CompetitionType, VolunteerType, Registration


class PassTypeAdmin(admin.ModelAdmin):
    pass


class CompetitionTypeAdmin(admin.ModelAdmin):
    pass


class VolunteerTypeAdmin(admin.ModelAdmin):
    pass


class RegistrationAdmin(admin.ModelAdmin):
    list_filter = ('pass_type',)


admin.site.register(PassType, PassTypeAdmin)
admin.site.register(CompetitionType, CompetitionTypeAdmin)
admin.site.register(VolunteerType, VolunteerTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
