from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^notif/$', views.mollie_notif, name='mollie_notif'),
]
