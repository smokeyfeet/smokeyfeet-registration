from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.landing, name='landing'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^status/(?P<registration_id>[0-9a-z-]+)/$', views.status, name='status'),
    url(r'^mollie_notif/', views.mollie_notif, name='mollie_notif'),
]
