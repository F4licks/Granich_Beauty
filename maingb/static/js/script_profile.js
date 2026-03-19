// Дополнительные скрипты для профиля
document.addEventListener('DOMContentLoaded', function () {
  // Автофокус на первый инпут
  const firstInput = document.querySelector('.form-control');
  if (firstInput) {
    firstInput.focus();
  }
  
  // Проверка валидности формы при отправке
  const profileForm = document.querySelector('form');
  if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
      const inputs = this.querySelectorAll('.form-control');
      let isValid = true;
      
      inputs.forEach(input => {
        if (!input.value.trim()) {
          input.style.borderColor = '#f44336';
          isValid = false;
        } else {
          input.style.borderColor = '#e0e0e0';
        }
      });
      
      if (!isValid) {
        e.preventDefault();
       Пожалуйста, заполните все поля');
      }
    });
  }
});