from django.urls import path
from . import views

app_name = 'maingb'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/ajax-update/', views.ajax_update_cart, name='ajax_update_cart'),
    
    # Профиль и аккаунт
    path('profile/', views.profile_view, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]