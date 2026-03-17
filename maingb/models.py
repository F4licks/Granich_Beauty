# maingb/models.py
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

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
    description = RichTextField(
        verbose_name="Описание",
        config_name='default'
    )
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
    name = models.CharField("Название пункта", max_length=255)
    address = models.TextField("Адрес")
    phone = models.CharField("Телефон", max_length=20, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт доставки"
        verbose_name_plural = "Пункты доставки"

    def __str__(self):
        return f"{self.name} - {self.address[:50]}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтверждён'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Контактные данные
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email")
    
    # Доставка
    delivery_point = models.ForeignKey(
        DeliveryPoint, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Пункт доставки"
    )
    delivery_address = models.TextField("Адрес доставки", blank=True)
    delivery_type = models.CharField(
        "Тип доставки",
        max_length=20,
        choices=[('pickup', 'Самовывоз'), ('delivery', 'Доставка')],
        default='pickup'
    )
    
    # Статус и оплата
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField("Сумма заказа", max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField("Оплачен", default=False)
    payment_method = models.CharField(
        "Способ оплаты",
        max_length=20,
        choices=[('cash', 'Наличные'), ('card', 'Карта')],
        default='cash'
    )
    
    # Комментарий
    comment = models.TextField("Комментарий", blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

    def calculate_total(self):
        """Пересчитывает общую сумму заказа"""
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    product_name = models.CharField("Название товара", max_length=255)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    def get_total_price(self):
        if self.price is None:
            return 0
        return self.price * self.quantity


class SiteSettings(models.Model):
    # Флаги отображения
    show_email = models.BooleanField("Показывать email", default=True)
    show_phone = models.BooleanField("Показывать телефон", default=True)
    show_address = models.BooleanField("Показывать адрес", default=True)

    # Контактные данные
    email = models.EmailField("Электронная почта", blank=True)
    phone = models.CharField("Контактный телефон", max_length=20, blank=True)
    address = models.TextField("Адрес", blank=True)

    class Meta:
        verbose_name = "Контактные данные"
        verbose_name_plural = "Контактные данные"

    def __str__(self):
        return "Контактные данные сайта"

    def save(self, *args, **kwargs):
        # Гарантируем, что будет только одна запись
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj