import base64
import binascii
import hashlib
import hmac
import json

import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Min, Prefetch, Sum, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from account.models import CartItem, WishlistItem, PATTERN_PRICES, SIZE_CHOICES
from .forms import ReviewForm
from .models import Order, OrderItem, Review, ReviewMedia, Shoes, ShoesVariant,Category,Brand
from .recommendations import get_recommendation_engine



class ShoesListView(View):
    def get(self, request, category_id=None):
        shoes = Shoes.objects.select_related("category", "brand").annotate(
            min_price=Min("variants__price"),
            total_stock=Sum("variants__stock_quantity"),
            avg_rating=Avg("reviews__rating"),
        )

        search = request.GET.get("searched", "").strip()

        category_ids = []

        if category_id is not None:
            category_ids.append(str(category_id))

        for val in request.GET.getlist("category"):
            category_ids.extend(
                [c.strip() for c in val.split(",") if c.strip()]
            )

        if category_ids:
            shoes = shoes.filter(category_id__in=category_ids)

        brand_ids = []
        for val in request.GET.getlist("brand"):
            brand_ids.extend(
                [b.strip() for b in val.split(",") if b.strip()]
            )

        if brand_ids:
            shoes = shoes.filter(brand_id__in=brand_ids)

        if search:
            shoes = shoes.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(category__name__icontains=search)
                | Q(brand__name__icontains=search)
            )

        stock = request.GET.get("stock")
        if stock == "instock":
            shoes = shoes.filter(total_stock__gt=0)

        rating = request.GET.get("rating")
        if rating and rating.isdigit():
            rating = int(rating)

            if rating == 5:
                shoes = shoes.filter(
                    avg_rating__gte=5,
                    avg_rating__lte=5
                )
            elif 1 <= rating <= 4:
                shoes = shoes.filter(
                    avg_rating__gte=rating,
                    avg_rating__lt=rating + 1
                )

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        if min_price:
            try:
                shoes = shoes.filter(min_price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                shoes = shoes.filter(min_price__lte=float(max_price))
            except ValueError:
                pass

        shoes = shoes.order_by("-created_at")

        paginator = Paginator(shoes, 9)
        page = request.GET.get("page", 1)
        shoes_list = paginator.get_page(page)

        categories = Category.objects.all().order_by("name")
        brands = Brand.objects.all().order_by("name")

        context = {
            "shoes_list": shoes_list,
            "query": search,
            "categories": categories,
            "brands": brands,
            "selected_categories": category_ids,
            "selected_brands": brand_ids,
            "selected_rating": rating if rating else "",
            "min_price": min_price,
            "max_price": max_price,
        }

        return render(request, "shoes/shoes_list.html", context)
        
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

        engine = get_recommendation_engine(request)
        engine.log_view(shoe)

        similar_shoes = engine.get_similar_shoes(shoe, limit=4)
        recommended_shoes = engine.get_recommendations(limit=4)

        context = {
            'shoe': shoe,
            'variants': variants,
            'variants_data': variants_data,
            'colors': colors,
            'selected_variant': selected_variant,
            'brand_shoes': brand_shoes,
            'similar_shoes': similar_shoes,
            'recommended_shoes': recommended_shoes,
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



MAX_QTY = 10  
FREE_SHIPPING_THRESHOLD = 3000

VALID_SIZES = {s for s, _ in SIZE_CHOICES}

PATTERN_PHOTOS = {
    "nike-converse-low-top": "img/patterns/converse-low-top.jpg",
    "nike-converse-high-top": "img/patterns/converse-high-top.jpg",
    "air-runner": "img/patterns/air-runner.jpg",
}


def _parse_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


def _error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def _serialize_item(item):
    if item.variant_id:
        v = item.variant
        photo_url = v.shoes_photo.url if v.shoes_photo else static('images/shoe_default.jpg')
        return {
            "id": item.id,
            "name": v.shoe.name,
            "meta": "",
            "color": v.color.name,
            "size": v.size.size_value,
            "price": str(item.unit_price),
            "photo": photo_url,
            "stock": v.stock_quantity,
            "quantity": item.quantity,
            "customization": [],
            "line_total": str(item.subtotal),
        }

    photo_url = (
        item.photo.url if item.photo
        else static(PATTERN_PHOTOS.get(item.pattern, "img/patterns/default.jpg"))
    )
    return {
        "id": item.id,
        "name": item.pattern_display_name,
        "meta": f"Size {item.size}",
        "size": item.size,
        "price": str(item.unit_price),
        "photo": photo_url,
        "stock": MAX_QTY,
        "quantity": item.quantity,
        "customization": [
            {"label": zone, "color": color} for zone, color in (item.colors or {}).items()
        ],
        "line_total": str(item.subtotal),
    }


def _cart_payload(user):
    items = list(CartItem.objects.filter(user=user))
    count = sum(i.quantity for i in items)
    subtotal = sum(i.subtotal for i in items)
    shipping_label = "—" if not items else (
        "Free" if subtotal >= FREE_SHIPPING_THRESHOLD else "Calculated at checkout"
    )
    return {
        "items": [_serialize_item(i) for i in items],
        "count": count,
        "subtotal": str(subtotal),
        "shipping_label": shipping_label,
        "shipping_fee": "0",
        "total": str(subtotal),
    }


def cart_page(request):
    return render(request, "shoes/cart.html")


@login_required
@require_GET
def cart_item_list(request):
    return JsonResponse(_cart_payload(request.user))


@login_required
@require_POST
@transaction.atomic
def cart_add(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={request.path}")

        pattern = request.GET.get('pattern')
        size = str(request.GET.get('size', ''))
        try:
            colors = json.loads(request.GET.get('colors', '{}'))
        except json.JSONDecodeError:
            colors = {}
        quantity = int(request.GET.get('quantity') or 1)

        if pattern not in PATTERN_PRICES or size not in VALID_SIZES:
            messages.error(request, 'Please choose a valid shoe and size.')
            return redirect(request.META.get('HTTP_REFERER', 'shoes:cart_page'))

        candidates = CartItem.objects.filter(user=request.user, pattern=pattern, size=size)
        match = next((i for i in candidates if i.colors == colors), None)
        if match:
            match.quantity = min(match.quantity + quantity, MAX_QTY)
            match.save()
        else:
            CartItem.objects.create(
                user=request.user, pattern=pattern, size=size,
                colors=colors, quantity=min(quantity, MAX_QTY),
            )
        return redirect('shoes:cart_page')

    data = _parse_body(request)

    variant_id = data.get("variant_id")
    if variant_id:
        return _add_variant_item(request, data, variant_id)

    pattern = data.get("pattern")
    size = str(data.get("size", ""))
    colors = data.get("colors") or {}
    quantity = int(data.get("quantity") or 1)

    if pattern not in PATTERN_PRICES:
        return _error("Unknown shoe pattern.")
    if size not in VALID_SIZES:
        return _error("Invalid size.")
    if quantity < 1:
        return _error("Quantity must be at least 1.")

    candidates = CartItem.objects.filter(user=request.user, pattern=pattern, size=size)
    match = next((i for i in candidates if i.colors == colors), None)

    if match:
        match.quantity = min(match.quantity + quantity, MAX_QTY)
        match.save()
    else:
        item = CartItem.objects.create(
            user=request.user,
            pattern=pattern,
            size=size,
            colors=colors,
            quantity=min(quantity, MAX_QTY),
        )
        photo_data_url = data.get("photo")
        photo_file = _decode_photo(photo_data_url, pattern)
        if photo_file:
            item.photo.save(photo_file.name, photo_file, save=True)

    return JsonResponse(_cart_payload(request.user))


def _add_variant_item(request, data, variant_id):
    try:
        quantity = int(data.get("quantity") or 1)
    except (TypeError, ValueError):
        return _error("Invalid quantity.")
    if quantity < 1:
        return _error("Quantity must be at least 1.")

    try:
        variant = ShoesVariant.objects.select_related('shoe', 'color', 'size').get(pk=variant_id)
    except ShoesVariant.DoesNotExist:
        return _error("Please choose a valid shoe.", status=404)

    if variant.stock_quantity < 1:
        return _error("That size is out of stock.")

    cap = min(MAX_QTY, variant.stock_quantity)
    match = CartItem.objects.filter(user=request.user, variant=variant).first()

    if match:
        match.quantity = min(match.quantity + quantity, cap)
        match.save()
    else:
        CartItem.objects.create(
            user=request.user,
            variant=variant,
            quantity=min(quantity, cap),
        )

    return JsonResponse(_cart_payload(request.user))


@login_required
@require_POST
@transaction.atomic
def cart_update(request):
    data = _parse_body(request)
    item_id = data.get("item_id")
    quantity = data.get("quantity")

    if item_id is None or quantity is None:
        return _error("item_id and quantity are required.")

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return _error("Invalid quantity.")

    try:
        item = CartItem.objects.get(id=item_id, user=request.user)
    except CartItem.DoesNotExist:
        return _error("Item not found in your cart.", status=404)

    item.quantity = max(1, min(quantity, MAX_QTY))
    item.save()

    return JsonResponse(_cart_payload(request.user))


@login_required
@require_POST
def cart_remove(request):
    data = _parse_body(request)
    item_id = data.get("item_id")
    if item_id is None:
        return _error("item_id is required.")

    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return JsonResponse(_cart_payload(request.user))


@login_required
@require_POST
def cart_clear(request):
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse(_cart_payload(request.user))

# ---------------------------------------------------------------
# Wishlist views
#
# Mirrors the CartItem/cart_* pattern above. Key difference: no
# unit_price snapshotting (see WishlistItem.price property for why),
# and a `wishlist_toggle` endpoint for the heart button, since a
# shoe card just needs "on/off" rather than separate add/remove calls.
# ---------------------------------------------------------------

def _serialize_wishlist_item(item):
    if item.variant_id:
        v = item.variant
        photo_url = v.shoes_photo.url if v.shoes_photo else static('images/shoe_default.jpg')
        return {
            "id": item.id,
            "variant_id": item.variant_id,
            "name": v.shoe.name,
            "meta": "",
            "color": v.color.name,
            "size": v.size.size_value,
            "price": str(item.price),
            "photo": photo_url,
            "stock": v.stock_quantity,
            "customization": [],
        }

    photo_url = item.photo.url if item.photo else static(PATTERN_PHOTOS.get(item.pattern, "img/patterns/default.jpg"))
    return {
        "id": item.id,
        "pattern": item.pattern,
        "name": item.pattern_display_name,
        "meta": f"Size {item.size}",
        "size": item.size,
        "price": str(item.price),
        "photo": photo_url,
        "stock": MAX_QTY,
        "customization": [
            {"label": zone, "color": color} for zone, color in (item.colors or {}).items()
        ],
    }


def _wishlist_payload(user):
    items = list(WishlistItem.objects.filter(user=user).select_related(
        'variant__shoe', 'variant__color', 'variant__size'
    ))
    return {
        "items": [_serialize_wishlist_item(i) for i in items],
        "count": len(items),
    }


def wishlist_page(request):
    return render(request, "shoes/wishlist.html")


@login_required
@require_GET
def wishlist_item_list(request):
    return JsonResponse(_wishlist_payload(request.user))


@login_required
@require_POST
def wishlist_add(request):
    data = _parse_body(request)
    variant_id = data.get("variant_id")

    if variant_id:
        try:
            variant = ShoesVariant.objects.get(pk=variant_id)
        except ShoesVariant.DoesNotExist:
            return _error("Please choose a valid shoe.", status=404)

        WishlistItem.objects.get_or_create(user=request.user, variant=variant)
        return JsonResponse(_wishlist_payload(request.user))

    pattern = data.get("pattern")
    size = str(data.get("size", ""))
    colors = data.get("colors") or {}

    if pattern not in PATTERN_PRICES:
        return _error("Unknown shoe pattern.")

    candidates = WishlistItem.objects.filter(user=request.user, pattern=pattern, size=size)
    match = next((i for i in candidates if i.colors == colors), None)
    if not match:
        item = WishlistItem.objects.create(
            user=request.user, pattern=pattern, size=size, colors=colors,
        )
        photo_data_url = data.get("photo")
        photo_file = _decode_photo(photo_data_url, pattern)
        if photo_file:
            item.photo.save(photo_file.name, photo_file, save=True)

    return JsonResponse(_wishlist_payload(request.user))


@login_required
@require_POST
def wishlist_remove(request):
    data = _parse_body(request)
    item_id = data.get("item_id")
    if item_id is None:
        return _error("item_id is required.")

    WishlistItem.objects.filter(id=item_id, user=request.user).delete()
    return JsonResponse(_wishlist_payload(request.user))


@login_required
@require_POST
def wishlist_toggle(request):
    """Add/remove in one call — used by the heart button on shoe cards.
    Accepts EITHER variant_id (admin-added shoes with a specific color/size)
    OR pattern (customizer-designed shoes shown before size/colors are
    chosen, e.g. on the homepage best-sellers grid)."""
    data = _parse_body(request)
    variant_id = data.get("variant_id")
    pattern = data.get("pattern")

    if variant_id:
        try:
            variant = ShoesVariant.objects.get(pk=variant_id)
        except ShoesVariant.DoesNotExist:
            return _error("Please choose a valid shoe.", status=404)

        existing = WishlistItem.objects.filter(user=request.user, variant=variant).first()
        if existing:
            existing.delete()
            is_wishlisted = False
        else:
            WishlistItem.objects.create(user=request.user, variant=variant)
            is_wishlisted = True

    elif pattern:
        if pattern not in PATTERN_PRICES:
            return _error("Unknown shoe pattern.")

        existing = WishlistItem.objects.filter(
            user=request.user, pattern=pattern, size="", colors={}
        ).first()
        if existing:
            existing.delete()
            is_wishlisted = False
        else:
            WishlistItem.objects.create(user=request.user, pattern=pattern, size="", colors={})
            is_wishlisted = True

    else:
        return _error("variant_id or pattern is required.")

    payload = _wishlist_payload(request.user)
    payload["is_wishlisted"] = is_wishlisted
    return JsonResponse(payload)


@login_required
@require_POST
@transaction.atomic
def wishlist_move_to_cart(request):
    data = _parse_body(request)
    item_id = data.get("item_id")
    if item_id is None:
        return _error("item_id is required.")

    try:
        item = WishlistItem.objects.get(id=item_id, user=request.user)
    except WishlistItem.DoesNotExist:
        return _error("Item not found in your wishlist.", status=404)

    if item.variant_id:
        variant = item.variant
        if variant.stock_quantity < 1:
            return _error("That size is out of stock.")
        cap = min(MAX_QTY, variant.stock_quantity)
        cart_match = CartItem.objects.filter(user=request.user, variant=variant).first()
        if cart_match:
            cart_match.quantity = min(cart_match.quantity + 1, cap)
            cart_match.save()
        else:
            CartItem.objects.create(user=request.user, variant=variant, quantity=1)
    else:
        cart_candidates = CartItem.objects.filter(
            user=request.user, pattern=item.pattern, size=item.size
        )
        cart_match = next((i for i in cart_candidates if i.colors == item.colors), None)
        if cart_match:
            cart_match.quantity = min(cart_match.quantity + 1, MAX_QTY)
            cart_match.save()
        else:
            new_cart_item = CartItem.objects.create(
                user=request.user, pattern=item.pattern, size=item.size,
                colors=item.colors, quantity=1,
            )
            if item.photo:
                new_cart_item.photo.save(
                    item.photo.name.split('/')[-1], item.photo.file, save=True
                )

    item.delete()
    return JsonResponse(_wishlist_payload(request.user))


def _decode_photo(data_url, pattern):
    if not data_url or ';base64,' not in data_url:
        return None
    header, encoded = data_url.split(';base64,', 1)
    ext = header.split('/')[-1]
    try:
        decoded = base64.b64decode(encoded)
    except (TypeError, ValueError):
        return None
    return ContentFile(decoded, name=f'{pattern}-snapshot.{ext}')


def checkout_view(request):
    return render(request, 'shoes/checkout.html')


def order_tracking_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order_id': order.order_id,
        'status': order.status,
        'payment_method': order.get_payment_method_display(),
        'total_amount': order.total_amount,
        'address': f"{order.address}, {order.city}",
    }
    return render(request, 'shoes/order_tracking.html', context)


def payment_success_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order_id': order.order_id,
        'total_amount': order.total_amount,
        'payment_method': order.get_payment_method_display(),
    }
    return render(request, 'shoes/payment_success.html', context)



STATUS_STEP = {
    'pending_payment': 0,
    'paid': 1,
    'processing': 1,
    'shipped': 2,
    'delivered': 3,
}

STATUS_BADGE_CLASS = {
    'pending_payment': 'pending',
    'paid': 'processing',
    'processing': 'processing',
    'shipped': 'shipped',
    'delivered': 'delivered',
    'cancelled': 'cancelled',
    'failed': 'cancelled',
}
@login_required
def order_history_view(request):
    status_filter = request.GET.get('status', 'all')

    orders_qs = Order.objects.filter(user=request.user).prefetch_related(
        'items__variant__shoe',
        'items__variant__color',
        'items__variant__size',
    ).order_by('-created_at')

    total_count = orders_qs.count()

    if status_filter != 'all':
        orders_qs = orders_qs.filter(status=status_filter)

    order_rows = []
    for order in orders_qs:
        order_rows.append({
            'order': order,
            'items': order.items.all(),
            'step_index': STATUS_STEP.get(order.status, 0),
            'is_failed': order.status == 'failed',
            'is_cancelled': order.status == 'cancelled',
            'can_cancel': order.status == 'pending_payment',
            'badge_class': STATUS_BADGE_CLASS.get(order.status, 'pending'),
        })

    context = {
        'order_rows': order_rows,
        'total_count': total_count,
        'status_filter': status_filter,
    }
    return render(request, 'history/history.html', context)


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status != 'pending_payment':
        messages.error(request, "This order can no longer be cancelled — it's already being processed.")
    else:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Order {order.order_id} has been cancelled.")

    return redirect('shoes:history')



@login_required
def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body)
    address = data['address']
    payment_method = data['payment_method']

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return JsonResponse({'error': 'Your cart is empty.'}, status=400)

    total_amount = 0
    for item in cart_items:
        if item.variant_id and item.quantity > item.variant.stock_quantity:
            return JsonResponse({'error': f'{item.variant} is out of stock'}, status=400)
        total_amount += item.subtotal

    order = Order.objects.create(
        user=request.user,
        full_name=address['full_name'],
        phone=address['phone'],
        address=address['address'],
        city=address['city'],
        landmark=address.get('landmark', ''),
        payment_method=payment_method,
        total_amount=total_amount,
    )

    for item in cart_items:
        if item.variant_id:
            OrderItem.objects.create(
                order=order, variant=item.variant,
                price=item.unit_price, quantity=item.quantity,
            )

    cart_items.delete()

    return JsonResponse({'order_id': order.order_id, 'total_amount': str(total_amount)})


def esewa_initiate(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    total_amount = str(order.total_amount)
    transaction_uuid = order.order_id
    product_code = settings.ESEWA_PRODUCT_CODE

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = base64.b64encode(
        hmac.new(settings.ESEWA_SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()

    context = {
        'amount': total_amount,
        'tax_amount': '0',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': request.build_absolute_uri(f'/shoes/payments/esewa/verify/{order.order_id}/'),
        'failure_url': request.build_absolute_uri('/shoes/checkout/'),
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
        'esewa_form_url': settings.ESEWA_FORM_URL,
    }
    return render(request, 'shoes/esewa_redirect.html', context)


def esewa_verify(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    encoded = request.GET.get('data')
    if not encoded:
        order.status = 'failed'
        order.save()
        return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')

    decoded = json.loads(base64.b64decode(encoded))
    if decoded.get('status') != 'COMPLETE':
        order.status = 'failed'
        order.save()
        return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')

    params = {
        'product_code': settings.ESEWA_PRODUCT_CODE,
        'total_amount': str(order.total_amount),
        'transaction_uuid': order.order_id,
    }
    result = requests.get(settings.ESEWA_STATUS_URL, params=params).json()

    if result.get('status') == 'COMPLETE':
        order.status = 'paid'
        order.transaction_id = decoded.get('transaction_code', '')
        order.save()
        return redirect(f'/shoes/orders/{order.order_id}/success/')

    order.status = 'failed'
    order.save()
    return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')


def khalti_initiate(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    payload = {
        "return_url": request.build_absolute_uri(f'/shoes/payments/khalti/verify/{order.order_id}/'),
        "website_url": request.build_absolute_uri('/'),
        "amount": int(order.total_amount * 100),
        "purchase_order_id": order.order_id,
        "purchase_order_name": f"SIMP Order {order.order_id}",
        "customer_info": {
            "name": order.full_name,
            "phone": order.phone,
        },
    }
    headers = {
        "Authorization": f"key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(settings.KHALTI_INITIATE_URL, json=payload, headers=headers)
    result = resp.json()

    if resp.status_code == 200 and 'payment_url' in result:
        return redirect(result['payment_url'])

    order.status = 'failed'
    order.save()
    return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')


def khalti_verify(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    pidx = request.GET.get('pidx')

    headers = {
        "Authorization": f"key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    result = requests.post(settings.KHALTI_LOOKUP_URL, json={"pidx": pidx}, headers=headers).json()

    if result.get('status') == 'Completed':
        order.status = 'paid'
        order.transaction_id = result.get('transaction_id', '')
        order.save()
        return redirect(f'/shoes/orders/{order.order_id}/success/')

    order.status = 'failed'
    order.save()
    return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')