from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('acrylic_powder', 'Акриловая пудра'),
    ('gel', 'Гель'),
    ('modeling_gel', 'Гель для моделирования ногтей'),
    ('gel_paint', 'Гель-краска для ногтей'),
    ('gel_lacquer', 'Гель-лак'),
    ('decor', 'Декор для маникюра'),
    ('top_coat', 'Закрепитель для гель-лака'),
    ('tools', 'Инструмент для маникюра и Педикюра'),
    ('brushes', 'Кисть для дизайна ногтей'),
    ('nail_glue', 'Клей для ногтей'),
    ('corrector', 'Корректор'),
    ('uv_lamp', 'Лампа для сушки ногтей'),
    ('magnet', 'Магнит для маникюра'),
    ('manicure_set', 'Маникюрный набор'),
    ('cosmetic_soap', 'Мыло косметическое'),
    ('press_on_nails', 'Накладные ногти'),
    ('false_eyelashes', 'Накладные ресницы'),
    ('base_gel_lacquer', 'Основа под гель-лак'),
    ('base_lacquer', 'Основа под лак'),
    ('nail_file', 'Пилка для ногтей'),
    ('mascara', 'Тушь'),
    ('cosmetic_brush', 'Щетка косметическая'),
]

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(help_text="Поддержка HTML")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True)
    default_address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nickname or self.user.username}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"


class DeliveryPoint(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название пункта")
    address = models.TextField(verbose_name="Адрес")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.name} — {self.address[:30]}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('collecting', 'Товар собирается'),
        ('shipped', 'Передан в доставку'),
        ('in_transit', 'В пути'),
        ('ready', 'Готов к выдаче'),
        ('delivered', 'Получен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_point = models.ForeignKey(DeliveryPoint, on_delete=models.PROTECT, verbose_name="Пункт выдачи")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итого")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='collecting', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # цена на момент заказа

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"