// maingb/static/js/script_home.js

document.addEventListener('DOMContentLoaded', function () {
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

  // Инициализация сворачивания
  initDescriptionToggles();

  // ========== Обработчик клика на изображение ==========
  window.handleImageClick = function(element) {
    try {
      const images = JSON.parse(element.dataset.images);
      const index = parseInt(element.dataset.index);
      openModal(images, index);
    } catch (e) {
      console.error('Ошибка при открытии модального окна:', e);
    }
  };

  // ========== Модальное окно для фото ==========
  let currentImageIndex = 0;
  let currentImages = [];

  window.openModal = function(images, index) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const modalDots = document.getElementById('modalDots');
    
    currentImages = images || [];
    currentImageIndex = index || 0;
    
    // Показываем модальное окно
    modal.style.display = 'flex';
    
    // Устанавливаем текущее изображение
    updateModalImage();
    
    // Показываем стрелки, если фото больше одного
    if (images && images.length > 1) {
      prevBtn.style.display = 'block';
      nextBtn.style.display = 'block';
    } else {
      prevBtn.style.display = 'none';
      nextBtn.style.display = 'none';
    }
    
    // Создаем точки-индикаторы
    modalDots.innerHTML = '';
    if (images) {
      images.forEach((_, i) => {
        const dot = document.createElement('span');
        dot.style.width = '10px';
        dot.style.height = '10px';
        dot.style.borderRadius = '50%';
        dot.style.background = i === index ? 'white' : 'rgba(255,255,255,0.5)';
        dot.style.cursor = 'pointer';
        dot.addEventListener('click', () => {
          currentImageIndex = i;
          updateModalImage();
        });
        modalDots.appendChild(dot);
      });
    }
  };

  function updateModalImage() {
    const modalImage = document.getElementById('modalImage');
    const modalDots = document.getElementById('modalDots');
    
    if (currentImages[currentImageIndex]) {
      modalImage.src = currentImages[currentImageIndex];
      
      // Обновляем точки
      const dots = modalDots.querySelectorAll('span');
      dots.forEach((dot, i) => {
        dot.style.background = i === currentImageIndex ? 'white' : 'rgba(255,255,255,0.5)';
      });
    }
  }

  function closeModal() {
    document.getElementById('imageModal').style.display = 'none';
    currentImages = [];
    currentImageIndex = 0;
  }

  // Закрытие по клику на фон
  const modal = document.getElementById('imageModal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === this) {
        closeModal();
      }
    });
  }

  // Закрытие по кнопке
  const closeModalBtn = document.getElementById('closeModal');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeModal);
  }

  // Навигация стрелками
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  
  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
      updateModalImage();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      currentImageIndex = (currentImageIndex + 1) % currentImages.length;
      updateModalImage();
    });
  }

  // Навигация клавиатурой
  document.addEventListener('keydown', function(e) {
    if (document.getElementById('imageModal')?.style.display === 'flex') {
      if (e.key === 'Escape') {
        closeModal();
      } else if (e.key === 'ArrowLeft') {
        currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
        updateModalImage();
      } else if (e.key === 'ArrowRight') {
        currentImageIndex = (currentImageIndex + 1) % currentImages.length;
        updateModalImage();
      }
    }
  });

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
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if (!csrftoken) {
      console.error('CSRF token не найден');
      return;
    }
    
    // ИСПРАВЛЕНО: используем window.urls.ajax_update_cart вместо {% url %}
    fetch(window.urls.ajax_update_cart, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: `product_id=${productId}&action=${action}`
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "removed") {
        card.querySelector('.product-actions').innerHTML = `
          <button class="cart-add btn btn-primary">В корзину</button>
        `;
      } else if (data.status === "updated") {
        card.querySelector('.product-actions').innerHTML = `
          <div class="cart-counter" style="display: flex; align-items: center; gap: 0.5rem;">
            <button class="cart-dec btn btn-outline" style="width: 30px;">−</button>
            <span class="cart-qty" style="font-weight: bold;">${data.item_count}</span>
            <button class="cart-inc btn btn-outline" style="width: 30px;">+</button>
          </div>
        `;
      }
      
      const badge = document.getElementById('cart-count');
      if (badge) {
        badge.textContent = data.cart_count;
        badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
      }
      
      attachListeners(card);
    })
    .catch(err => console.error("Ошибка при обновлении корзины:", err));
  }

  document.querySelectorAll('.product-card').forEach(card => attachListeners(card));
});