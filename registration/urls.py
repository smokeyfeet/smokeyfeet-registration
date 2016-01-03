from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.landing, name='landing'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^complete/(.+)/$', views.complete, name='complete'),
    url(r'^status/(.+)/$', views.status, name='status'),
    url(r'^mollie_notif/', views.mollie_notif, name='mollie_notif'),
]
