// maingb/static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
  // Карусель товаров
  const carousels = document.querySelectorAll('.carousel');
  carousels.forEach(carousel => {
    const items = carousel.querySelectorAll('.carousel-item');
    const dots = carousel.querySelectorAll('.carousel-dot');
    let currentIndex = 0;

    function showSlide(index) {
      items.forEach(item => item.classList.remove('active'));
      dots.forEach(dot => dot.classList.remove('active'));

      items[index].classList.add('active');
      dots[index].classList.add('active');
    }

    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        currentIndex = index;
        showSlide(currentIndex);
      });
    });

    // Авто-переключение каждые 4 сек
    setInterval(() => {
      currentIndex = (currentIndex + 1) % items.length;
      showSlide(currentIndex);
    }, 4000);

    showSlide(0);
  });

  // Корзина
  const cartBtn = document.querySelector('#cart-btn');
  const cartSidebar = document.querySelector('.cart-sidebar');
  const cartOverlay = document.querySelector('.cart-overlay');
  const closeCartBtn = document.querySelector('#close-cart');

  if (cartBtn) {
    cartBtn.addEventListener('click', () => {
      cartSidebar.classList.add('open');
      cartOverlay.classList.add('show');
    });
  }

  if (closeCartBtn) {
    closeCartBtn.addEventListener('click', () => {
      cartSidebar.classList.remove('open');
      cartOverlay.classList.remove('show');
    });
  }

  cartOverlay.addEventListener('click', () => {
    cartSidebar.classList.remove('open');
    cartOverlay.classList.remove('show');
  });

  // Кнопки +/- в корзине (если они будут динамически добавлены)
  document.addEventListener('click', function (e) {
    if (e.target.classList.contains('qty-minus')) {
      const input = e.target.closest('.qty-control').querySelector('input');
      if (parseInt(input.value) > 1) input.value--;
    } else if (e.target.classList.contains('qty-plus')) {
      const input = e.target.closest('.qty-control').querySelector('input');
      input.value++;
    }
  });

  // Показать количество в кнопке корзины
  function updateCartBadge(count) {
    const badge = document.querySelector('#cart-count');
    if (badge) {
      badge.textContent = count > 0 ? count : '';
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
  }

  // Инициализация количества (можно обновлять через AJAX позже)
  const initialCount = parseInt(document.querySelector('#cart-count')?.textContent) || 0;
  updateCartBadge(initialCount);
});