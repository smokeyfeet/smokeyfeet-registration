from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import urls as auth_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include(auth_urls)),
    path("", include("smokeyfeet.registration.urls", namespace="registration")),
    path(
        "mollie/", include("smokeyfeet.mollie_webhook.urls", namespace="mollie_webhook")
    ),
    path("shop/", include("smokeyfeet.minishop.urls", namespace="minishop")),
]
