from django.contrib import admin
from .models import Product, ProductImage, UserProfile, Address, CartItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at')
    inlines = [ProductImageInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'default_address')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'address_line', 'is_default')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')