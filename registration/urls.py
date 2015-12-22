from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^complete/(.+)/$', views.complete, name='complete'),
    url(r'^done/(.+)/$', views.done, name='done'),
    url(r'^mollie_notif/', views.mollie_notif, name='mollie_notif'),
]
