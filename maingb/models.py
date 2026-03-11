from django.db import models
from django.contrib.auth.models import User

# Список категорий
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
        verbose_name="Категория (для фильтрации)"
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


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    address_line = models.TextField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} — {self.address_line[:30]}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"