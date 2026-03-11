# maingb/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm as BasePasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, Address

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'default_address')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('title', 'address_line', 'is_default')

class PasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})