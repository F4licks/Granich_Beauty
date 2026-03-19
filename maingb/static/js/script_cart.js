document.addEventListener('DOMContentLoaded', function () {
  // Функция пересчёта общей суммы
  function updateTotal() {
    let total = 0;
    document.querySelectorAll('.cart-item-row').forEach(row => {
      const qty = parseInt(row.querySelector('.qty-value').textContent);
      const price = parseFloat(row.dataset.price);
      total += qty * price;
    });
    
    const totalEl = document.getElementById('cart-total');
    if (totalEl) {
      totalEl.textContent = total.toFixed(2) + ' ₽';
    }
  }

  // Функция обновления товара через AJAX
  function updateCartItem(productId, action, row) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch("{% url 'maingb:ajax_update_cart' %}", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `product_id=${productId}&action=${action}`
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "removed") {
        row.remove();
      } else if (data.status === "updated") {
        row.querySelector('.qty-value').textContent = data.item_count;
        row.querySelector('.qty-value-display').textContent = data.item_count;
      }

      const badge = document.getElementById('cart-count');
      if (badge) {
        badge.textContent = data.cart_count;
        badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
      }

      updateTotal();
    })
    .catch(err => console.error("Ошибка при обновлении корзины:", err));
  }

  // Назначить обработчики на кнопки "+"
  document.querySelectorAll('.qty-inc').forEach(btn => {
    btn.addEventListener('click', function () {
      const row = this.closest('.cart-item-row');
      const productId = row.dataset.productId;
      updateCartItem(productId, 'add', row);
    });
  });

  // Назначить обработчики на кнопки "-"
  document.querySelectorAll('.qty-dec').forEach(btn => {
    btn.addEventListener('click', function () {
      const row = this.closest('.cart-item-row');
      const productId = row.dataset.productId;
      updateCartItem(productId, 'remove', row);
    });
  });

  // Инициализация: рассчитать сумму при загрузке
  updateTotal();
});