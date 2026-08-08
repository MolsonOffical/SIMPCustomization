from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db.models import Q


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
    created_at = models.DateTimeField(auto_now_add=True)
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
    'air-jordan-1': 5200,
    'low-poly-boot': 4100,
    'urban-canvas': 3800,
}

PATTERN_NAMES = {
    'nike-converse-low-top': 'Converse Custom Chuck Taylor — Low Top',
    'nike-converse-high-top': 'Converse Custom Chuck Taylor — High Top',
    'air-runner': 'Air Runner',
    'air-jordan-1': 'Air Jordan 1',
    'low-poly-boot': 'Low Poly Boot',
    'urban-canvas': 'Urban Canvas',
}

SIZE_CHOICES = [(str(s), str(s)) for s in range(6, 12)]





class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )

    # --- Customizer-designed shoe fields (all optional now) ---
    pattern = models.CharField(max_length=64, blank=True, null=True)
    size = models.CharField(max_length=8, blank=True, null=True)
    # Per-zone color selections from the customizer, e.g.
    # {"Outside Body": "#B50024", "Laces": "#40E0D0", ...}
    colors = models.JSONField(default=dict, blank=True)

    # --- Admin-added regular shoe field (new) ---
    variant = models.ForeignKey(
        'shoes.ShoesVariant',
        on_delete=models.CASCADE,
        related_name='cart_items',
        null=True,
        blank=True,
    )

    quantity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    # Snapshot of the price at the time the item was added, so later
    # price changes don't retroactively change what's already in a cart.
    unit_price = models.PositiveIntegerField(editable=False)
    photo = models.ImageField(upload_to='cart_photos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(pattern__isnull=False) | Q(variant__isnull=False),
                name='cartitem_has_pattern_or_variant',
                )
    ]

    def save(self, *args, **kwargs):
        if not self.unit_price:
            if self.variant_id:
                self.unit_price = int(self.variant.price)
            else:
                self.unit_price = PATTERN_PRICES.get(self.pattern, 0)
        super().save(*args, **kwargs)

    @property
    def is_variant_item(self):
        return self.variant_id is not None

    @property
    def pattern_display_name(self):
        return PATTERN_NAMES.get(self.pattern, self.pattern)

    @property
    def display_name(self):
        if self.variant_id:
            return self.variant.shoe.name
        return self.pattern_display_name

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        if self.variant_id:
            return f"{self.user} — {self.variant} x{self.quantity}"
        return f"{self.user} — {self.pattern_display_name} (size {self.size}) x{self.quantity}"
class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
    )

    # --- Customizer-designed shoe fields (mirrors CartItem) ---
    pattern = models.CharField(max_length=64, blank=True, null=True)
    size = models.CharField(max_length=8, blank=True, null=True)
    colors = models.JSONField(default=dict, blank=True)
    photo = models.ImageField(upload_to='wishlist_photos/', blank=True, null=True)

    # --- Admin-added regular shoe field ---
    variant = models.ForeignKey(
        'shoes.ShoesVariant',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(pattern__isnull=False) | Q(variant__isnull=False),
                name='wishlistitem_has_pattern_or_variant',
            ),
            # Prevent the same admin-added variant being wishlisted twice by
            # the same user. Customizer items aren't uniqued this way since
            # two saved designs on the same pattern can have different colors.
            models.UniqueConstraint(
                fields=['user', 'variant'],
                condition=Q(variant__isnull=False),
                name='unique_wishlist_variant_per_user',
            ),
        ]

    @property
    def is_variant_item(self):
        return self.variant_id is not None

    @property
    def pattern_display_name(self):
        return PATTERN_NAMES.get(self.pattern, self.pattern)

    @property
    def display_name(self):
        if self.variant_id:
            return self.variant.shoe.name
        return self.pattern_display_name

    @property
    def price(self):
        # Unlike CartItem, no snapshotting — a wishlist isn't a transaction,
        # so it's fine (arguably better) to always show the current price.
        if self.variant_id:
            return self.variant.price
        return PATTERN_PRICES.get(self.pattern, 0)

    def __str__(self):
        if self.variant_id:
            return f"{self.user} ♥ {self.variant}"
        return f"{self.user} ♥ {self.pattern_display_name}"