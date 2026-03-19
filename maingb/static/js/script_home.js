// ========== Сворачивание описания ==========
function initDescriptionToggles() {
  document.querySelectorAll('.product-desc-content').forEach(content => {
    const wrapper = content.parentElement;
    const button = wrapper.nextElementSibling;
    
    if (!button || !button.classList.contains('toggle-desc-btn')) return;
    
    // Рассчитываем максимальную высоту для 4 строк
    const lineHeight = parseFloat(getComputedStyle(content).lineHeight) || 24;
    const maxHeight = 4 * lineHeight;
    const fullHeight = content.scrollHeight;
    
    if (fullHeight > maxHeight) {
      // Нужно свернуть
      content.style.maxHeight = maxHeight + 'px';
      content.style.overflow = 'hidden';
      content.style.position = 'relative';
      
      // Добавляем градиентное затемнение
      const gradient = document.createElement('div');
      gradient.className = 'desc-gradient';
      gradient.style.cssText = `
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: ${lineHeight}px;
        background: linear-gradient(to top, rgba(255,255,255,1) 30%, rgba(255,255,255,0) 100%);
      `;
      content.appendChild(gradient);
      
      button.style.display = 'block';
      
      // Обработчик клика
      button.onclick = function() {
        const isExpanded = this.getAttribute('data-expanded') === 'true';
        
        if (isExpanded) {
          // Сворачиваем
          content.style.maxHeight = maxHeight + 'px';
          content.style.overflow = 'hidden';
          gradient.style.display = 'block';
          this.textContent = 'Подробнее';
          this.setAttribute('data-expanded', 'false');
        } else {
          // Развертываем
          content.style.maxHeight = 'none';
          content.style.overflow = 'visible';
          gradient.style.display = 'none';
          this.textContent = 'Свернуть';
          this.setAttribute('data-expanded', 'true');
        }
      };
    } else {
      // Не нужно сворачивать
      button.style.display = 'none';
    }
  });
}

// ========== AJAX-корзина ==========
function attachListeners(card) {
  const productId = card.dataset.productId;
  const addBtn = card.querySelector('.cart-add');
  const incBtn = card.querySelector('.cart-inc');
  const decBtn = card.querySelector('.cart-dec');

  if (addBtn) {
    addBtn.onclick = () => updateCart(productId, 'add', card);
  }
  if (incBtn) {
    incBtn.onclick = () => updateCart(productId, 'add', card);
  }
  if (decBtn) {
    decBtn.onclick = () => updateCart(productId, 'remove', card);
  }
}

function updateCart(productId, action, card) {
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  
  fetch('/cart/ajax-update/', {
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
      // Товар удалён из корзины
      card.querySelector('.product-actions').innerHTML = `
        <button class="cart-add btn btn-primary" style="width: 100%; padding: 1rem; font-size: 1.1rem;">В корзину</button>
      `;
    } else if (data.status === "updated") {
      // Товар добавлен/изменён
      card.querySelector('.product-actions').innerHTML = `
        <div class="cart-counter" style="display: flex; align-items: center; gap: 0.5rem;">
          <button class="cart-dec btn btn-outline" style="width: 40px; height: 40px; border-radius: 50%; font-size: 1.2rem;">−</button>
          <span class="cart-qty" style="font-weight: bold; font-size: 1.2rem;">${data.item_count}</span>
          <button class="cart-inc btn btn-outline" style="width: 40px; height: 40px; border-radius: 50%; font-size: 1.2rem;">+</button>
        </div>
      `;
    }
    
    // Обновляем счётчик в шапке
    const badge = document.getElementById('cart-count');
    if (badge) {
      badge.textContent = data.cart_count;
      badge.style.display = data.cart_count > 0 ? 'inline-flex' : 'none';
    }
    
    // Переприкрепляем обработчики к новым кнопкам
    attachListeners(card);
  })
  .catch(err => {
    console.error("Ошибка:", err);
    alert('Произошла ошибка при добавлении в корзину');
  });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
  // Инициализация сворачивания описаний
  initDescriptionToggles();
  
  // Инициализация кнопок корзины
  document.querySelectorAll('.product-card').forEach(card => {
    attachListeners(card);
  });
});