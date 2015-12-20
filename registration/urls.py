from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^complete/([0-9]+)/$', views.complete, name='complete'),
    url(r'^done/([0-9]+)/$', views.complete, name='done'),
    url(r'^mollie_notif/', views.mollie_notif, name='mollie_notif'),
]
