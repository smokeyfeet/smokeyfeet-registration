from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Product


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = (
        "first_name", "last_name", "email", "created_at", "display_product")

    ordering = ("created_at",)

    def display_product(self, obj):
        qs = obj.items.all()
        return qs[0].product_name if qs.count else "none"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "num_in_stock", "unit_price")
