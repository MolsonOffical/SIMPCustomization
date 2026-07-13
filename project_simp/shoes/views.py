from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Min, Sum, Prefetch
from .models import Shoes, ShoesVariant
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.http import require_GET, require_POST

from account.models import CartItem, PATTERN_PRICES, SIZE_CHOICES
import base64
import binascii
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string


def _decode_photo(data_url):
    """
    data_url looks like: "data:image/png;base64,iVBORw0KGgoAAAANS..."
    Returns a Django ContentFile ready to assign to an ImageField, or
    None if there's nothing usable (missing, malformed, wrong scheme).
    """
    if not data_url or not isinstance(data_url, str) or not data_url.startswith("data:image"):
        return None
    try:
        header, encoded = data_url.split(",", 1)
        ext = header.split("/")[1].split(";")[0]  # "png", "jpeg", etc.
        decoded = base64.b64decode(encoded)
        filename = f"{get_random_string(12)}.{ext}"
        return ContentFile(decoded, name=filename)
    except (ValueError, IndexError, binascii.Error):
        return None

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

        context = {
            'shoe': shoe,
            'variants': variants,
            'variants_data': variants_data,
            'colors': colors,
            'selected_variant': selected_variant,
            'brand_shoes': brand_shoes,
            'similar_shoes': similar_shoes,
        }
        return render(request, 'shoes/shoe_detail.html', context)

def test(request):
    return render(request, "D:/projects/intern-codeit/SIMPCustomization\project_simp/templates/layout.html")


class History(View):
    def get(self, request, category_id=None):

        return render(request, 'history/history.html')
    
# shoes/views.py
#
# Cart views for the "shoes" app. The CartItem model itself lives in
# accounts/models.py (it's tied to CustomUser) — that's fine, Django
# apps are allowed to import each other's models. Just don't import
# anything from `shoes` back into `accounts` and you're safe from
# circular imports.



MAX_QTY = 10  # matches MaxValueValidator(10) on CartItem.quantity
FREE_SHIPPING_THRESHOLD = 3000

VALID_SIZES = {s for s, _ in SIZE_CHOICES}

# Representative photo per pattern (a base product shot, used as a
# fallback when a CartItem has no saved custom-preview photo).
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
        # dict -> list so cart.html's existing renderCustomizationDots()
        # works unchanged: [{"label": "Laces", "color": "#40E0D0"}, ...]
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


# ------------------------------------------------------------- page -------

def cart_page(request):
    return render(request, "shoes/cart.html")


# ------------------------------------------------------------- read -------

@login_required
@require_GET
def cart_item_list(request):
    return JsonResponse(_cart_payload(request.user))


# -------------------------------------------------------------- add -------

@login_required
@require_POST
@transaction.atomic
def cart_add(request):
    data = _parse_body(request)
    pattern = data.get("pattern")
    size = str(data.get("size", ""))
    colors = data.get("colors") or {}
    quantity = int(data.get("quantity") or 1)
    photo_file = _decode_photo(data.get("photo"))

    if pattern not in PATTERN_PRICES:
        return _error("Unknown shoe pattern.")
    if size not in VALID_SIZES:
        return _error("Invalid size.")
    if quantity < 1:
        return _error("Quantity must be at least 1.")

    # Same pattern + size + exact same colors -> bump quantity on that
    # line instead of creating a duplicate row.
    candidates = CartItem.objects.filter(user=request.user, pattern=pattern, size=size)
    match = next((i for i in candidates if i.colors == colors), None)

    if match:
        match.quantity = min(match.quantity + quantity, MAX_QTY)
        if photo_file:
            match.photo = photo_file
        match.save()
    else:
        CartItem.objects.create(
            user=request.user,
            pattern=pattern,
            size=size,
            colors=colors,
            quantity=min(quantity, MAX_QTY),
            photo=photo_file,
        )

    return JsonResponse(_cart_payload(request.user))


# ------------------------------------------------------------ update ------

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


# ------------------------------------------------------------ remove ------

@login_required
@require_POST
def cart_remove(request):
    data = _parse_body(request)
    item_id = data.get("item_id")
    if item_id is None:
        return _error("item_id is required.")

    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return JsonResponse(_cart_payload(request.user))


# ------------------------------------------------------------- clear ------

@login_required
@require_POST
def cart_clear(request):
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse(_cart_payload(request.user))