from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Prefetch
from django.contrib.auth.models import User
from .models import Product, CartItem, UserProfile, CATEGORY_CHOICES, SiteSettings, DeliveryPoint, Order, OrderItem
from .forms import RegisterForm, ProfileForm, PasswordChangeForm


def get_cart_count(user):
    if user.is_authenticated:
        total = CartItem.objects.filter(user=user).aggregate(total=Sum('quantity'))['total']
        return total or 0
    return 0


def home(request):
    products = Product.objects.prefetch_related('images')
    
    category = request.GET.get('category')
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if category:
        products = products.filter(category=category)
    if query:
        products = products.filter(name__icontains=query)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    if request.user.is_authenticated:
        cart_prefetch = Prefetch(
            'cartitem_set',
            queryset=CartItem.objects.filter(user=request.user),
            to_attr='cart_items'
        )
        products = products.prefetch_related(cart_prefetch, 'images')
    else:
        products = products.prefetch_related('images')

    used_categories = products.values_list('category', flat=True).distinct()
    category_choices = [(code, label) for code, label in CATEGORY_CHOICES if code in used_categories]
    
    site_settings = SiteSettings.load()

    context = {
        'products': products,
        'cart_count': get_cart_count(request.user),
        'categories': category_choices,
        'selected_category': category,
        'search_query': query or '',
        'sort': sort or '',
        'price_min': price_min or '',
        'price_max': price_max or '',
        'site_settings': site_settings,
    }
    return render(request, 'home.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'product_detail.html', context)


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'cart.html', context)


@login_required
def ajax_update_cart(request):
    if request.method != "POST":
        return JsonResponse({"error": "Только POST"}, status=400)

    product_id = request.POST.get("product_id")
    action = request.POST.get("action")

    if not product_id:
        return JsonResponse({"error": "Нет product_id"}, status=400)

    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1}
    )

    if action == "add":
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    elif action == "remove":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            return JsonResponse({
                "status": "removed",
                "cart_count": get_cart_count(request.user),
                "item_count": 0,
                "product_price": float(product.price)
            })
    else:
        return JsonResponse({"error": "Неизвестное действие"}, status=400)

    return JsonResponse({
        "status": "updated",
        "cart_count": get_cart_count(request.user),
        "item_count": cart_item.quantity,
        "product_price": float(product.price)
    })


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.error(request, "Корзина пуста.")
        return redirect('maingb:cart')

    delivery_points = DeliveryPoint.objects.filter(is_active=True)

    if request.method == 'POST':
        delivery_id = request.POST.get('delivery_point')
        payment_method = request.POST.get('payment_method')

        if not delivery_id:
            messages.error(request, "Выберите пункт выдачи.")
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'delivery_points': delivery_points,
                'total': sum(item.product.price * item.quantity for item in cart_items)
            })

        try:
            delivery_point = DeliveryPoint.objects.get(id=delivery_id, is_active=True)
        except DeliveryPoint.DoesNotExist:
            messages.error(request, "Неверный пункт выдачи.")
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'delivery_points': delivery_points,
                'total': sum(item.product.price * item.quantity for item in cart_items)
            })

        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(
            user=request.user,
            delivery_point=delivery_point,
            total_amount=total,
            status='collecting'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()
        messages.success(request, "Заказ оформлен!")
        return redirect('maingb:home')

    total = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'delivery_points': delivery_points,
        'total': total,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'checkout.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('maingb:home')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'login.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f"Аккаунт {user.username} создан!")
            return redirect('maingb:profile')
        else:
            messages.error(request, "Ошибка при регистрации.")
    else:
        form = RegisterForm()
    context = {
        'form': form,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'register.html', context)


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=profile, user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Профиль обновлён.")
                return redirect('maingb:profile')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Пароль изменён.")
                return redirect('maingb:profile')
            else:
                messages.error(request, "Ошибка при смене пароля.")

    else:
        profile_form = ProfileForm(instance=profile, user=request.user)
        password_form = PasswordChangeForm(user=request.user)

    # Заказы пользователя
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'password_form': password_form,
        'orders': orders,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'profile.html', context)


def logout_view(request):
    logout(request)
    return redirect('maingb:home')