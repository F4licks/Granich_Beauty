from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Prefetch
from django.contrib.auth.models import User
from .models import Product, CartItem, Address, UserProfile
from .forms import RegisterForm, ProfileForm, AddressForm, PasswordChangeForm


def get_cart_count(user):
    if user.is_authenticated:
        total = CartItem.objects.filter(user=user).aggregate(total=Sum('quantity'))['total']
        return total or 0
    return 0


def home(request):
    if request.user.is_authenticated:
        cart_prefetch = Prefetch(
            'cartitem_set',
            queryset=CartItem.objects.filter(user=request.user),
            to_attr='cart_items'
        )
        products = Product.objects.prefetch_related(cart_prefetch).all()
    else:
        products = Product.objects.all()
    
    context = {
        'products': products,
        'cart_count': get_cart_count(request.user),
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
    addresses = Address.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
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
                "product_price": float(product.price),
                "item_count": 0
            })
    else:
        return JsonResponse({"error": "Неизвестное действие"}, status=400)

    return JsonResponse({
        "status": "updated",
        "cart_count": get_cart_count(request.user),
        "item_count": cart_item.quantity,
        "product_price": float(product.price)
    })


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
            profile_form = ProfileForm(request.POST, instance=profile)
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

        elif 'add_address' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                addr = address_form.save(commit=False)
                addr.user = request.user
                addr.save()
                messages.success(request, "Адрес добавлен.")
                return redirect('maingb:profile')

        elif 'set_default' in request.POST:
            addr_id = request.POST.get('set_default')
            Address.objects.filter(user=request.user).update(is_default=False)
            Address.objects.filter(id=addr_id, user=request.user).update(is_default=True)
            messages.success(request, "Адрес по умолчанию изменён.")
            return redirect('maingb:profile')

        elif 'delete_addr' in request.POST:
            addr_id = request.POST.get('delete_addr')
            Address.objects.filter(id=addr_id, user=request.user).delete()
            messages.success(request, "Адрес удалён.")
            return redirect('maingb:profile')

    profile_form = ProfileForm(instance=profile)
    address_form = AddressForm()
    password_form = PasswordChangeForm(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'address_form': address_form,
        'password_form': password_form,
        'addresses': addresses,
        'cart_count': get_cart_count(request.user),
    }
    return render(request, 'profile.html', context)


def logout_view(request):
    logout(request)
    return redirect('maingb:home')