import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


CUSTOMIZER_CHOICES = [
    ('nike-converse-low-top', 'Converse Low Top'),
    ('nike-converse-high-top', 'Converse High Top'),
    ('air-runner', 'Air Runner'),
    ('air-jordan-1', 'Air Jordan 1'),
    ('low-poly-boot', 'Low Poly Boot'),
    ('urban-canvas', 'Urban Canvas'),
]


class Shoes(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="shoes")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="shoes")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="shoes/thumbnails/", blank=True, null=True)
    customizer_id = models.CharField(
        max_length=64, choices=CUSTOMIZER_CHOICES, blank=True, null=True,
        help_text="Which 3D customizer model this catalog shoe should open."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Shoes"

    def __str__(self):
        return self.name


class ShoesColor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ShoesSize(models.Model):
    size_value = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.size_value


class ShoesVariant(models.Model):
    shoe = models.ForeignKey(Shoes, on_delete=models.CASCADE, related_name="variants")
    color = models.ForeignKey(ShoesColor, on_delete=models.CASCADE)
    size = models.ForeignKey(ShoesSize, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    shoes_photo = models.ImageField(upload_to="shoes/images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("shoe", "color", "size")

    def __str__(self):
        return f"{self.shoe.name} - {self.color.name} - {self.size.size_value}"


class Review(models.Model):
    shoe = models.ForeignKey(Shoes, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("shoe", "user")

    def __str__(self):
        return f"{self.user} → {self.shoe} ({self.rating}★)"


def review_media_upload_path(instance, filename):
    return f"reviews/{instance.review.shoe_id}/{instance.review.user_id}/{filename}"


class ReviewMedia(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to=review_media_upload_path)
    media_type = models.CharField(
        max_length=5,
        choices=[('image', 'Image'), ('video', 'Video')],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ReviewReply(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name="reply")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.review}"


class ShoeView(models.Model):
    shoe = models.ForeignKey(Shoes, on_delete=models.CASCADE, related_name="shoe_views")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shoe_views",
    )
    visitor_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["shoe", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["visitor_id", "created_at"]),
        ]

    def __str__(self):
        who = f"user:{self.user_id}" if self.user_id else f"visitor:{self.visitor_id}"
        return f"View({self.shoe_id} by {who})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    PAYMENT_CHOICES = [('esewa', 'eSewa'), ('khalti', 'Khalti')]

    order_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, blank=True)

    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = "SIMP" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    # Catalog shoe (nullable now — customizer items don't have a variant)
    variant = models.ForeignKey(
        ShoesVariant, on_delete=models.PROTECT, related_name='order_items',
        null=True, blank=True,
    )

    # Customizer shoe fields (nullable — catalog items don't use these)
    pattern = models.CharField(max_length=64, blank=True, null=True)
    colors = models.JSONField(default=dict, blank=True)
    size = models.CharField(max_length=8, blank=True, null=True)
    photo = models.ImageField(upload_to='order_photos/', blank=True, null=True)


    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at time of order
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.price * self.quantity

    @property
    def display_photo_url(self):
        if self.photo:
            return self.photo.url
        if self.variant_id and self.variant.shoes_photo:
            return self.variant.shoes_photo.url
        return None

    def __str__(self):
        if self.variant_id:
            return f"{self.variant} x{self.quantity}"
        return f"{self.pattern} (size {self.size}) x{self.quantity}"

