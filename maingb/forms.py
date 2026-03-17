# maingb/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm as BasePasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ('nickname', 'default_address')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ← извлекаем user из kwargs
        super().__init__(*args, **kwargs)
        
        # Заполняем поле email текущим значением из пользователя
        if self.user and self.user.email:
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Проверяем, что user передан
        if not self.user:
            raise forms.ValidationError("Ошибка: пользователь не определён")
        
        if email:
            # Проверяем, что этот email не используется другим пользователем
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("Этот email уже используется другим пользователем")
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Сохраняем email в модель пользователя
        email = self.cleaned_data.get('email')
        if email and self.user:
            self.user.email = email
            self.user.save()
        
        if commit:
            instance.save()
        return instance

class PasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})