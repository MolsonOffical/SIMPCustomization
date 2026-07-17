import json
import hmac
import hashlib
import base64
import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Min, Sum, Prefetch
from .models import Shoes, ShoesVariant, Order, OrderItem
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




class CartView(View):
    def get(self, request):
        # Cart contents are rendered client-side from localStorage by cart.js,
        # this view just needs to serve the template shell.
        return render(request, 'shoes/cart.html')


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
        match.save()
    else:
        CartItem.objects.create(
            user=request.user,
            pattern=pattern,
            size=size,
            colors=colors,
            quantity=min(quantity, MAX_QTY),
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


# ---------------------------------------------------------------
# Order creation
# ---------------------------------------------------------------

def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body)
    address = data['address']
    items = data['items']  # [{variant_id, quantity}, ...]
    payment_method = data['payment_method']

    order_items = []
    total_amount = 0
    for item in items:
        variant = get_object_or_404(ShoesVariant, id=item['variant_id'])
        quantity = int(item['quantity'])
        if quantity > variant.stock_quantity:
            return JsonResponse({'error': f'{variant} is out of stock'}, status=400)
        total_amount += float(variant.price) * quantity
        order_items.append((variant, quantity))

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=address['full_name'],
        phone=address['phone'],
        address=address['address'],
        city=address['city'],
        landmark=address.get('landmark', ''),
        payment_method=payment_method,
        total_amount=total_amount,
    )
    for variant, quantity in order_items:
        OrderItem.objects.create(order=order, variant=variant, price=variant.price, quantity=quantity)

    return JsonResponse({'order_id': order.order_id, 'total_amount': str(total_amount)})


# ---------------------------------------------------------------
# eSewa (ePay v2) — UAT/test credentials, see settings.py
# ---------------------------------------------------------------

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

    # Defense in depth: re-check with eSewa's status API before trusting the callback
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
        return redirect(f'/shoes/orders/{order.order_id}/track/?status=paid')

    order.status = 'failed'
    order.save()
    return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')


# ---------------------------------------------------------------
# Khalti (KPG v2) — sandbox test key, see settings.py
# ---------------------------------------------------------------

def khalti_initiate(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    payload = {
        "return_url": request.build_absolute_uri(f'/shoes/payments/khalti/verify/{order.order_id}/'),
        "website_url": request.build_absolute_uri('/'),
        "amount": int(order.total_amount * 100),  # Khalti expects paisa
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
        return redirect(f'/shoes/orders/{order.order_id}/track/?status=paid')

    order.status = 'failed'
    order.save()
    return redirect(f'/shoes/orders/{order.order_id}/track/?status=failed')