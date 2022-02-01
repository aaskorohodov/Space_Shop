from django import forms
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import *


class RegisterUserForm(UserCreationForm):
    '''Форма для регистрации нового пользователя. Переменные ниже указывают стили для этих полей.'''
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    '''Форма авторизации'''
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class AddComment(forms.ModelForm):
    CHOICES = [(1, ''),
               (2, ''),
               (3, ''),
               (4, ''),
               (5, '')]

    user = forms.CharField(required=False, label='Пользователь', widget=forms.TextInput(attrs={'placeholder': 'Аноним'}))
    rating = forms.ChoiceField(required=False, choices=CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = Comments  # указывает, с какой моделью установить связь
        fields = ['text', 'user', 'rating'] # какие поля брать


class MakeOrder(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['paid', 'delivery', 'user', 'canceled', 'closed']


class ChangePass(forms.Form):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput())
    new_password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput())
    new_password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())


class AddUserPhoto(forms.ModelForm):
    class Meta:
        model = UserExtra
        fields = ['user_photo']


