from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.catalog, name='catalog'),
    url(r'^cart/$', views.cart, name='cart'),
    url(r'^order/(\d+)/$', views.order, name='order'),
    url(r'^mollie_notif/$', views.mollie_notif, name='mollie_notif'),
]
