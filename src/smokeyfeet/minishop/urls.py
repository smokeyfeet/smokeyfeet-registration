from django.urls import path
from django.urls import re_path

from . import views

app_name = "minishop"
urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("cart/", views.cart, name="cart"),
    re_path(r"^order/(?P<order_id>[0-9a-z-]+)/$", views.order, name="order"),
]
