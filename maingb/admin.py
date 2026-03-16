from django.contrib import admin
from .models import Product, ProductImage, UserProfile, CartItem, DeliveryPoint, Order, OrderItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'get_category_display', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)
    inlines = [ProductImageInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')


@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'delivery_point', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'delivery_point')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'total_amount', 'created_at')