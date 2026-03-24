# maingb/admin.py
from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import (
    Product, ProductImage, 
    SiteSettings, DeliveryPoint, Order, OrderItem
)

# ========== Product (Товары) ==========
class ProductAdminForm(forms.ModelForm):
    """Форма с визуальным редактором для описания"""
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
        }

class ProductImageInline(admin.TabularInline):
    """Изображения товара во вложенном виде"""
    model = ProductImage
    extra = 1
    fields = ('image', 'order')
    show_change_link = True
    verbose_name = "Изображение"
    verbose_name_plural = "Изображения товара"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'price', 'get_category_display', 'created_at')
    list_display_links = ('name',)
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'description', 'price', 'category'),
            'classes': ('wide',)
        }),
        ('Дополнительно', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    # Иконка для jazzmin (если установлен)
    jazzmin_icon = 'fas fa-box-open'


# ========== Order (Заказы) ==========
class OrderItemInline(admin.TabularInline):
    """Товары в заказе (только для просмотра)"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'get_total_price')
    can_delete = False
    show_change_link = True
    verbose_name = "Товар в заказе"
    verbose_name_plural = "Товары в заказе"
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    get_total_price.short_description = "Сумма"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status_badge', 'total_amount', 'created_at', 'is_paid_badge')
    list_display_links = ('id', 'user')
    list_filter = ('status', 'is_paid', 'delivery_type', 'created_at')
    search_fields = ('user__username', 'phone', 'email', 'delivery_address')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Заказчик', {
            'fields': ('user', 'phone', 'email'),
            'classes': ('wide',)
        }),
        ('Доставка', {
            'fields': ('delivery_type', 'delivery_point', 'delivery_address'),
            'classes': ('wide',)
        }),
        ('Оплата и статус', {
            'fields': ('status', 'is_paid', 'payment_method', 'total_amount'),
            'classes': ('wide',)
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Кастомные методы для цветных бейджей в списке
    def status_badge(self, obj):
        colors = {
            'pending': '#ff8f00',      # Оранжевый
            'confirmed': '#388e3c',    # Зеленый
            'shipped': '#1976d2',      # Синий
            'delivered': '#2e7d32',    # Темно-зеленый
            'cancelled': '#c62828',    # Красный
        }
        return f'<span style="padding: 3px 8px; border-radius: 12px; background: {colors.get(obj.status, "#757575")}; color: white; font-weight: 500;">{obj.get_status_display()}</span>'
    status_badge.short_description = "Статус"
    status_badge.allow_tags = True
    
    def is_paid_badge(self, obj):
        if obj.is_paid:
            return '<span style="padding: 3px 8px; border-radius: 12px; background: #388e3c; color: white; font-weight: 500;">Оплачено</span>'
        return '<span style="padding: 3px 8px; border-radius: 12px; background: #c62828; color: white; font-weight: 500;">Не оплачено</span>'
    is_paid_badge.short_description = "Оплата"
    is_paid_badge.allow_tags = True
    
    # Автоматический пересчет суммы при сохранении
    def save_model(self, request, obj, form, change):
        obj.calculate_total()
        super().save_model(request, obj, form, change)
    
    jazzmin_icon = 'fas fa-shopping-cart'


# ========== DeliveryPoint (Пункты выдачи) ==========
@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active_badge')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    ordering = ('name',)
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'address', 'phone', 'is_active')
        }),
    )
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return '<span style="padding: 3px 8px; border-radius: 12px; background: #388e3c; color: white; font-weight: 500;">Активен</span>'
        return '<span style="padding: 3px 8px; border-radius: 12px; background: #c62828; color: white; font-weight: 500;">Неактивен</span>'
    is_active_badge.short_description = "Статус"
    is_active_badge.allow_tags = True
    
    jazzmin_icon = 'fas fa-map-marker-alt'


# ========== SiteSettings (Контакты сайта) ==========
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Настройки отображения', {
            'fields': ('show_email', 'show_phone', 'show_address'),
            'description': '✅ Отметьте, какие контактные данные показывать на сайте',
            'classes': ('wide',)
        }),
        ('Контактные данные', {
            'fields': ('email', 'phone', 'address'),
            'classes': ('wide',)
        }),
    )
    
    # Разрешаем только одну запись
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    jazzmin_icon = 'fas fa-cog'


# ========== Скрытие ненужных моделей ==========
# Эти модели не регистрируются — они управляются через другие разделы:
# - UserProfile → через раздел Пользователи (auth.User)
# - CartItem → через корзину на сайте
# - OrderItem → уже отображается во вложенном виде в Order
# - ProductImage → уже отображается во вложенном виде в Product