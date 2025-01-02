from django.urls import path
from django.urls import re_path

from . import views

app_name = "registration"
urlpatterns = [
    path("", views.signup, name="signup"),
    path("thanks/", views.thanks, name="thanks"),
    re_path(r"^status/(?P<registration_id>[0-9a-z-]+)/$", views.status, name="status"),
    re_path(r"^registrations/", views.registrations, name="list"),
    re_path(
        r"^registration/(?P<registration_id>[0-9a-z-]+)/$",
        views.registration,
        name="detail",
    ),
]
