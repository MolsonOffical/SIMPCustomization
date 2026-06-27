import re
from django.core.exceptions import ValidationError

def validate_alphanumeric_username(value):
    if not value.isalnum():
        raise ValidationError("Username can only contain letters and numbers (no symbols).")

def validate_nepal_phone(value):
    pattern = r'^(?:(?:\+|00)?977\s?)?(98|97|91)\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid Nepal mobile number .")

def validate_image_size(file):
    max_size = 2 * 1024 * 1024  # 2MB
    if file and hasattr(file, 'size'):
        if file.size > max_size:
            raise ValidationError("Image size must be under 2MB.")

def validate_alpha_name(value):
    if not value.isalpha():
        raise ValidationError("This field can only contain letters (A-Z).")
