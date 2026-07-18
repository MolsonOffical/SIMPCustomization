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
from .recommendations import get_recommendation_engine


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
        }
        return render(request, 'shoes/shoe_detail.html', context)


def test(request):
    return render(request, "D:/projects/intern-codeit/SIMPCustomization\\project_simp/templates/layout.html")


class CartView(View):
    def get(self, request):
        # Cart contents are rendered client-side from localStorage by cart.js,
        # this view just needs to serve the template shell.
        return render(request, 'shoes/cart.html')


class History(View):
    def get(self, request, category_id=None):
        return render(request, 'history/history.html')


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