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

    list_filter = ('mollie_payment_status',)

    list_display = ('first_name', 'last_name', 'email', 'created_at')

    ordering = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
