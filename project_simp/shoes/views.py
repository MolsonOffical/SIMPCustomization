from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Min, Sum, Prefetch, Avg
from .models import Shoes, ShoesVariant
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import Review, ReviewMedia
from .forms import ReviewForm


class ShoesListView(View):
    def get(self, request, category_id=None):
        shoes = Shoes.objects.select_related(
            'category', 'brand'
        ).annotate(
            min_price=Min('variants__price'),
            total_stock=Sum('variants__stock_quantity'),
        )

        if category_id:
            shoes = shoes.filter(category_id=category_id)

        shoes = shoes.order_by('-created_at')
        paginator = Paginator(shoes, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'shoes/shoes_list.html', {'shoes_list': page_obj})


class ShoeDetailView(View):
    def get(self, request, pk):
        variants_qs = ShoesVariant.objects.select_related(
            'color', 'size'
        ).order_by('color__name', 'size__size_value')

        shoe = get_object_or_404(
            Shoes.objects.select_related('category', 'brand').prefetch_related(
                Prefetch('variants', queryset=variants_qs)
            ),
            pk=pk
        )
        variants = list(shoe.variants.all())

        color_photo = {}
        for v in variants:
            if v.shoes_photo and v.color_id not in color_photo:
                color_photo[v.color_id] = v.shoes_photo.url

        for v in variants:
            v.resolved_photo = v.shoes_photo.url if v.shoes_photo else color_photo.get(
                v.color_id, '')

        variant_id = request.GET.get('variant')
        selected_variant = None
        if variant_id:
            selected_variant = next(
                (v for v in variants if str(v.pk) == variant_id), None)
        if not selected_variant and variants:
            in_stock = [v for v in variants if v.stock_quantity > 0]
            selected_variant = in_stock[0] if in_stock else variants[0]

        colors_seen = {}
        for v in variants:
            if v.color_id not in colors_seen:
                colors_seen[v.color_id] = v.color
        colors = list(colors_seen.values())
        for color in colors:
            color.display_thumbnail = color_photo.get(color.id, '')

        variants_data = [
            {
                'id': v.pk,
                'color_id': v.color_id,
                'size_id': v.size_id,
                'size_value': v.size.size_value,
                'price': str(v.price),
                'stock': v.stock_quantity,
                'photo': v.resolved_photo,
            }
            for v in variants
        ]

        brand_shoes = Shoes.objects.filter(
            brand=shoe.brand
        ).exclude(pk=pk).annotate(
            min_price=Min('variants__price')
        ).select_related('category', 'brand')[:4]

        similar_shoes = Shoes.objects.filter(
            category=shoe.category
        ).exclude(pk=pk).annotate(
            min_price=Min('variants__price')
        ).select_related('category', 'brand')[:4]
        reviews = shoe.reviews.select_related('user').prefetch_related('media').order_by('-created_at')
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        review_count = reviews.count()

        rating_breakdown = []
        for star in [5, 4, 3, 2, 1]:
            count = reviews.filter(rating=star).count()
            percent = round((count / review_count) * 100) if review_count else 0
            rating_breakdown.append({'star': star, 'count': count, 'percent': percent})

        user_has_reviewed = (
            request.user.is_authenticated
            and reviews.filter(user=request.user).exists()
        )

        context = {
            'shoe': shoe,
            'variants': variants,
            'variants_data': variants_data,
            'colors': colors,
            'selected_variant': selected_variant,
            'brand_shoes': brand_shoes,
            'similar_shoes': similar_shoes,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'rating_breakdown': rating_breakdown,
            'user_has_reviewed': user_has_reviewed,
            'review_form': ReviewForm(),
        }

        return render(request, 'shoes/shoe_detail.html', context)

def test(request):
    return render(request, "D:/projects/intern-codeit/SIMPCustomization\project_simp/templates/layout.html")
class CartView(View):
    def get(self, request):
        # Cart contents are rendered client-side from localStorage by cart.js,
        # this view just needs to serve the template shell.
        return render(request, 'shoes/cart.html')

class History(View):
    def get(self, request, category_id=None):

        return render(request, 'history/history.html')
    
class AddReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        shoe = get_object_or_404(Shoes, pk=pk)
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.shoe = shoe
            review.user = request.user
            review.save()

            for f in request.FILES.getlist('files'):
                media_type = 'video' if f.content_type.startswith('video') else 'image'
                ReviewMedia.objects.create(review=review, file=f, media_type=media_type)

            messages.success(request, "Review submitted.")
        else:
            error_text = "; ".join(
                f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()
            )
            messages.error(request, f"Couldn't submit review — {error_text}")
        return redirect('shoes:shoe_detail', pk=pk)
class EditReviewView(LoginRequiredMixin, View):
    def get(self, request, pk, review_id):
        review = get_object_or_404(Review, pk=review_id, shoe_id=pk)
        if review.user != request.user:
            messages.error(request, "You can't edit someone else's review.")
            return redirect('shoes:shoe_detail', pk=pk)
        form = ReviewForm(instance=review)
        return render(request, 'shoes/edit_review.html', {'form': form, 'shoe_id': pk, 'review_id': review_id, 'review': review})

    def post(self, request, pk, review_id):
        review = get_object_or_404(Review, pk=review_id, shoe_id=pk)
        if review.user != request.user:
            messages.error(request, "You can't edit someone else's review.")
            return redirect('shoes:shoe_detail', pk=pk)
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()

            remove_ids = request.POST.getlist('remove_media')
            if remove_ids:
                review.media.filter(id__in=remove_ids).delete()

            for f in request.FILES.getlist('new_files'):
                media_type = 'video' if f.content_type.startswith('video') else 'image'
                ReviewMedia.objects.create(review=review, file=f, media_type=media_type)

            messages.success(request, "Review updated.")
            return redirect('shoes:shoe_detail', pk=pk)
        return render(request, 'shoes/edit_review.html', {'form': form, 'shoe_id': pk, 'review_id': review_id, 'review': review})

class DeleteReviewView(LoginRequiredMixin, View):
    def post(self, request, pk, review_id):
        review = get_object_or_404(Review, pk=review_id, shoe_id=pk)
        if review.user != request.user:
            messages.error(request, "You can't delete someone else's review.")
        else:
            review.delete()
            messages.success(request, "Review deleted.")
        return redirect('shoes:shoe_detail', pk=pk)