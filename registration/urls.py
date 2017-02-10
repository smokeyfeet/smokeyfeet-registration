from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.signup, name='signup'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^status/(?P<registration_id>[0-9a-z-]+)/$', views.status, name='status'),
    url(r'^registrations/', views.registrations, name='list'),
    url(r'^registration/(?P<registration_id>[0-9a-z-]+)/$', views.registration, name='detail'),
]
