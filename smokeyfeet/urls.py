from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import urls as auth_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include(auth_urls)),
    path("/", include("registration.urls", namespace="registration")),
    path("mollie/", include("mollie_webhook.urls", namespace="mollie_webhook")),
    path("shop/", include("minishop.urls", namespace="minishop")),
]
