from django.db import models
from django.contrib.auth.models import AbstractUser
import os
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
    
#add to cart model

class CartItem(models.Model):
    """
    A single customized shoe sitting in a user's cart.

    Colors and pattern describe the customization the person made on the
    designer page. Price is stored per-item (not looked up live) so that if
    you change prices later, items already in someone's cart don't shift
    under them.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )

    name = models.CharField(max_length=100, default='Custom Shoe')
    size = models.CharField(max_length=10)
    pattern = models.CharField(max_length=20, blank=True)

    # Stores something like {"upper": "#1a7a4a", "sole": "#333333", ...}
    colors = models.JSONField(default=dict, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.size}) x{self.quantity} — {self.user}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
