from django.contrib import admin

from .models import PassType, Registration


class PassTypeAdmin(admin.ModelAdmin):
    pass


class RegistrationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PassType, PassTypeAdmin)
admin.site.register(Registration, RegistrationAdmin)
