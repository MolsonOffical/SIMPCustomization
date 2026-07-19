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


class Shoes(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="shoes")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="shoes")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="shoes/thumbnails/", blank=True, null=True)
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