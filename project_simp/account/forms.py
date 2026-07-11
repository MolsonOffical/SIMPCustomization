from django import forms
from .models import CustomUser,Address
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
class ProfileUpdateForm(forms.ModelForm):
    street_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Street address'}),
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City'}),
    )
    district = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'District'}),
    )
    province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Province'}),
    )
 
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'age',
            'gender',
            'banner',
            'profile',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '98XXXXXXXX'}),
            'age': forms.NumberInput(attrs={'min': 0}),
            'gender': forms.Select(choices=CustomUser.GENDER_CHOICES),
        }
 
    ADDRESS_FIELD_NAMES = ['street_address', 'city', 'district', 'province']
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
        if self.instance and self.instance.pk:
            existing_address = self.instance.addresses.first()
            if existing_address:
                self.fields['street_address'].initial = existing_address.street_address
                self.fields['city'].initial = existing_address.city
                self.fields['district'].initial = existing_address.district
                self.fields['province'].initial = existing_address.province
 
    def save(self, commit=True):
        user = super().save(commit=commit)
 
        street_address = self.cleaned_data.get('street_address')
        city = self.cleaned_data.get('city')
        district = self.cleaned_data.get('district')
        province = self.cleaned_data.get('province')
 
        # Only touch the Address row if at least one address field was filled in.
        if any([street_address, city, district, province]):
            address = user.addresses.first() or Address(user=user)
            address.street_address = street_address
            address.city = city
            address.district = district
            address.province = province
            address.save()
 
        return user