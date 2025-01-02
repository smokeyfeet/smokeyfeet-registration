from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Cart
from .models import CartItem
from .models import Order
from .models import OrderItem
from .models import Payment
from .models import Product


class OrderPaidFilter(admin.SimpleListFilter):
    title = _("has paid")

    parameter_name = "has_paid"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        ids = [order.id for order in queryset.all() if order.is_paid()]

        if self.value() == "yes":
            return queryset.filter(id__in=ids)

        if self.value() == "no":
            return queryset.exclude(id__in=ids)


class OrderBackorderFilter(admin.SimpleListFilter):
    title = _("on backorder")

    parameter_name = "on_backorder"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        ids = [order.id for order in queryset.all() if order.has_backorder_items()]

        if self.value() == "yes":
            return queryset.filter(id__in=ids)

        if self.value() == "no":
            return queryset.exclude(id__in=ids)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, PaymentInline]

    list_filter = (
        "created_at",
        "items__product",
        OrderPaidFilter,
        OrderBackorderFilter,
    )

    list_display = ("first_name", "last_name", "email", "created_at")

    ordering = ("created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "num_in_stock", "unit_price")
