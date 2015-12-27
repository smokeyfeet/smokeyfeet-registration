from django.contrib import admin

from .models import Registration


class RegistrationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Registration, RegistrationAdmin)
