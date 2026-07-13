from django.db.models import Sum
from .models import CartItem


def cart_context(request):
    """
    Makes `cart_item_count` available in every template automatically
    (e.g. for the navbar badge in layout.html), without every view
    needing to pass it manually.
    """
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).aggregate(
            total=Sum('quantity')
        )['total'] or 0
    else:
        count = 0
    return {'cart_item_count': count}