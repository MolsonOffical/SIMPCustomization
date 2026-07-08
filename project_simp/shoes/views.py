from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Min, Sum, Prefetch
from .models import Shoes, ShoesVariant


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
        variants_qs = ShoesVariant.objects.select_related('color', 'size').order_by('color__name', 'size__size_value')
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
            v.resolved_photo = v.shoes_photo.url if v.shoes_photo else color_photo.get(v.color_id, '')

        variant_id = request.GET.get('variant')
        selected_variant = None
        if variant_id:
            selected_variant = next((v for v in variants if str(v.pk) == variant_id), None)
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
        context = {
            'shoe': shoe,
            'variants': variants,
            'variants_data': variants_data,
            'colors': colors,
            'selected_variant': selected_variant,
        }
        return render(request, 'shoes/shoe_detail.html', context)


class CartView(View):
    def get(self, request):
        # Cart contents are rendered client-side from localStorage by cart.js,
        # this view just needs to serve the template shell.
        return render(request, 'shoes/cart.html')