document.addEventListener('DOMContentLoaded', function () {
  // ========== Модальное окно ==========
  let currentImageIndex = 0;
  let currentImages = [];

  window.openModal = function(images, index) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const modalDots = document.getElementById('modalDots');
    
    currentImages = images;
    currentImageIndex = index;
    
    modal.style.display = 'flex';
    updateModalImage();
    
    if (images.length > 1) {
      prevBtn.style.display = 'block';
      nextBtn.style.display = 'block';
    }
    
    modalDots.innerHTML = '';
    images.forEach((_, i) => {
      const dot = document.createElement('span');
      dot.style.cssText = `
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: ${i === index ? 'white' : 'rgba(255,255,255,0.5)'};
        cursor: pointer;
      `;
      dot.addEventListener('click', () => {
        currentImageIndex = i;
        updateModalImage();
      });
      modalDots.appendChild(dot);
    });
  }

  function updateModalImage() {
    const modalImage = document.getElementById('modalImage');
    const modalDots = document.getElementById('modalDots');
    
    if (currentImages[currentImageIndex]) {
      modalImage.src = currentImages[currentImageIndex];
      
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

  document.getElementById('imageModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
  });

  document.getElementById('closeModal').addEventListener('click', closeModal);

  document.getElementById('prevBtn').addEventListener('click', function() {
    currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
    updateModalImage();
  });

  document.getElementById('nextBtn').addEventListener('click', function() {
    currentImageIndex = (currentImageIndex + 1) % currentImages.length;
    updateModalImage();
  });

  document.addEventListener('keydown', function(e) {
    if (document.getElementById('imageModal').style.display === 'flex') {
      if (e.key === 'Escape') closeModal();
      else if (e.key === 'ArrowLeft') {
        currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
        updateModalImage();
      } else if (e.key === 'ArrowRight') {
        currentImageIndex = (currentImageIndex + 1) % currentImages.length;
        updateModalImage();
      }
    }
  });

  // Обработчик клика по фото
  document.querySelectorAll('.carousel-item').forEach(item => {
    item.addEventListener('click', function() {
      const imageIndex = parseInt(this.dataset.imageIndex);
      
      // Получаем все изображения товара
      const images = Array.from(document.querySelectorAll('.carousel-item img'))
        .map(img => img.src);
      
      openModal(images, imageIndex);
    });
  });

  // ========== AJAX-корзина ==========
  const productId = "{{ product.id }}";
  
  function updateCart(action) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch("{% url 'maingb:ajax_update_cart' %}", {
      method: "POST",
      headers: {"X-CSRFToken": csrftoken, "Content-Type": "application/x-www-form-urlencoded"},
      body: `product_id=${productId}&action=${action}`
    })
    .then(response => response.json())
    .then(data => {
      const actionsDiv = document.querySelector('.product-actions');
      if (data.status === "removed") {
        actionsDiv.innerHTML = `<button class="cart-add btn btn-primary" style="padding: 0.75rem 2rem; font-size: 1.1rem; border-radius: 8px;">В корзину</button>`;
        attachListeners();
      } else if (data.status === "updated") {
        actionsDiv.innerHTML = `
          <div class="cart-counter" style="display: flex; align-items: center; gap: 0.5rem;">
            <button class="cart-dec btn btn-outline" style="width: 36px; height: 36px;">−</button>
            <span class="cart-qty" style="font-weight: bold; font-size: 1.1rem; min-width: 30px; text-align: center;">${data.item_count}</span>
            <button class="cart-inc btn btn-outline" style="width: 36px; height: 36px;">+</button>
          </div>
        `;
        attachListeners();
      }

      const badge = document.getElementById('cart-count');
      if (badge) {
        badge.textContent = data.cart_count;
        badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
      }
    });
  }

  function attachListeners() {
    document.querySelector('.cart-add')?.addEventListener('click', () => updateCart('add'));
    document.querySelector('.cart-inc')?.addEventListener('click', () => updateCart('add'));
    document.querySelector('.cart-dec')?.addEventListener('click', () => updateCart('remove'));
  }

  attachListeners();
});