from django.urls import path

from . import views


app_name = "mollie_webhook"
urlpatterns = [path("notif/", views.mollie_notif, name="mollie_notif")]
