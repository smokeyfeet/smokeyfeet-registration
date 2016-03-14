from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.catalog, name='catalog'),
    url(r'^order/(\d+)/$', views.order, name='order'),
    url(r'^product/(\d+)/', views.product, name='product'),
    url(r'^cart/$', views.cart, name='cart'),
]
