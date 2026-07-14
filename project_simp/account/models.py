from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


# Create your models here.

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]
    age=models.PositiveIntegerField(default=18, blank=False,null=False)
    gender = models.CharField(max_length=14, choices=GENDER_CHOICES, blank=False, null=False)
    phone_number=models.CharField(max_length=15,blank=False,null=False)
    banner = models.ImageField(upload_to='banner/',blank=True,null=True)
    profile = models.ImageField(upload_to='profile/', blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
    
    def save(self, *args, **kwargs):
        try:
            old = CustomUser.objects.get(id=self.id)
        except CustomUser.DoesNotExist:
            old = None

        super().save(*args, **kwargs)

        if old:
            if old.profile and not self.profile:
                self.delete_file(old.profile)

            if old.banner and not self.banner:
                self.delete_file(old.banner)

    def delete_file(self, fieldfile):
        file_path = fieldfile.path
        if os.path.isfile(file_path):
            os.remove(file_path)
            
class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user} - {self.otp}"
    

class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.city}"
    

# account/models.py
# Add this to your existing account/models.py (keep your other models
# like User/Profile/etc. above or below this — this is only the
# cart-related part).

# Single source of truth for shoe prices — used by both the frontend
# (converse_customizer.js keeps its own copy for display-only purposes)
# and the backend (so a tampered client-side price can never be trusted).
PATTERN_PRICES = {
    'nike-converse-low-top': 5200,
    'nike-converse-high-top': 5600,
    'air-runner': 4500,
}

PATTERN_NAMES = {
    'nike-converse-low-top': 'Converse Custom Chuck Taylor — Low Top',
    'nike-converse-high-top': 'Converse Custom Chuck Taylor — High Top',
    'air-runner': 'Air Runner',
}

SIZE_CHOICES = [(str(s), str(s)) for s in range(6, 12)]


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    pattern = models.CharField(max_length=64)
    size = models.CharField(max_length=8, choices=SIZE_CHOICES)
    # Per-zone color selections from the customizer, e.g.
    # {"Outside Body": "#B50024", "Laces": "#40E0D0", ...}
    colors = models.JSONField(default=dict, blank=True)
    quantity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    # Snapshot of the price at the time the item was added, so later
    # price changes in PATTERN_PRICES don't retroactively change what's
    # already sitting in someone's cart.
    unit_price = models.PositiveIntegerField(editable=False)
    photo = models.ImageField(upload_to='cart_photos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = PATTERN_PRICES.get(self.pattern, 0)
        super().save(*args, **kwargs)

    @property
    def pattern_display_name(self):
        return PATTERN_NAMES.get(self.pattern, self.pattern)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


    def __str__(self):
        return f"{self.user} — {self.pattern_display_name} (size {self.size}) x{self.quantity}"

