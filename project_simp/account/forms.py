from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .validators import validate_alphanumeric_username, validate_nepal_phone, validate_image_size, validate_alpha_name
import re


class RegistrationForms(UserCreationForm):
    placeholders = {
        'username': 'Enter your username',
        'email': 'Enter your email',
        'age': 'Enter your age',
        'gender': 'Select your gender',
        'phone_number': 'Enter your phone number',
        'password1': 'Enter your password',
        'password2': 'Confirm your password',
    }

    labels = {
        'username': 'Username',
        'email': 'Email',
        'age': 'Age',
        'gender': 'Gender',
        'phone_number': 'Phone Number',
        'password1': 'Password',
        'password2': 'Confirm Password',
    }

    class Meta:
        model = CustomUser
        fields = ['username', 'age', 'gender', 'email', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            placeholder = self.placeholders.get(field_name, field.label)
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': placeholder,
                'id': f'id_{field_name}',
            })
            if field_name in self.labels:
                field.label = self.labels[field_name]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        validate_alphanumeric_username(username)
        return username

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 13 or age > 120):
            raise forms.ValidationError("Age must be between 13 and above.")
        return age

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            validate_nepal_phone(phone)
            phone = re.sub(r'^(?:\+|00)?977\s?', '', phone)
        return phone

    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        if profile:
            validate_image_size(profile)
        return profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
                'id': 'username',
            }
        )
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
                'id': 'password',
            }
        )
    )
