# maingb/admin.py
from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import (
    Product, ProductImage, UserProfile, CartItem, 
    SiteSettings, DeliveryPoint, Order, OrderItem
)

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(), 
        }

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Настройки отображения', {
            'fields': ('show_email', 'show_phone', 'show_address'),
            'description': 'Выберите, какие контактные данные показывать на сайте'
        }),
        ('Контактные данные', {
            'fields': ('email', 'phone', 'address')
        }),
    )


@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active')
    list_filter = ('is_active',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'get_total_price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at', 'is_paid')
    list_filter = ('status', 'is_paid', 'delivery_type', 'created_at')
    search_fields = ('user__username', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'status', 'is_paid', 'payment_method')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Доставка', {
            'fields': ('delivery_type', 'delivery_point', 'delivery_address')
        }),
        ('Сумма', {
            'fields': ('total_amount',)
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity', 'get_total_price')
    readonly_fields = ('get_total_price',)