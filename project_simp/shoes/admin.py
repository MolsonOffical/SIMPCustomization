from django.contrib import admin
from .models import Category, Brand, Shoes, ShoesColor, ShoesSize, ShoesVariant, Review, ReviewMedia, ReviewReply
# Register your models here.
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Shoes)
admin.site.register(ShoesColor)
admin.site.register(ShoesSize)
admin.site.register(ShoesVariant)


class ReviewMediaInline(admin.TabularInline):
    model = ReviewMedia
    extra = 0


class ReviewReplyInline(admin.StackedInline):
    model = ReviewReply
    extra = 0
    max_num = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('shoe', 'user', 'rating', 'is_anonymous', 'created_at')
    list_filter = ('rating', 'is_anonymous')
    search_fields = ('shoe__name', 'user__username', 'comment')
    inlines = [ReviewMediaInline, ReviewReplyInline]