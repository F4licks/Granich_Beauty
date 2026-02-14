from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(help_text="Поддержка HTML (например, <br>, <strong>)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})


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
    email_confirmed = models.BooleanField(default=False)
    # Добавим адреса доставки отдельно
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