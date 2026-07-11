from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForms, LoginForm, ProfileUpdateForm
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import login, logout, authenticate
from .services import create_and_send_otp, verify_otp
from shoes.models import Category
import json
from django.http import JsonResponse
from .models import CartItem
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST

# Create your views here.
class HomePage(View):
    def get(self, request):
       
        return render(request, 'Home/index.html')


class AboutPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('account:home')
        return render(request, 'Home/about.html')


class RegisterUser(View):
    def get(self, request):
        form = RegistrationForms()
        return render(request, 'register/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForms(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()             
            create_and_send_otp(user)
            request.session['pending_user_id'] = user.id            
            return redirect('account:send_otp')
        else:
            messages.error(request, 'Registration fail')
        return render(request, 'register/register.html', {'form': form})


class LoginUser(View):
    def get(self, request):
        form = LoginForm()
        context = {'form': form}
        if request.GET.get('from') == 'about' or request.GET.get('next'):
            context['show_login_message'] = True
        return render(request, 'login/login.html', context)

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser or user.is_staff:
                    messages.error(request, 'Admin/staff accounts cannot sign in here.')
                    return render(request, 'login/login.html', {'form': form})

                login(request, user)

                if not user.is_email_verified:
                    return redirect('account:send_otp')

                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('account:home')

            else:
                messages.error(request, 'Error something went wrong.')
        else:
            messages.error(request, 'Username or Password is invalid.')
        return render(request, 'login/login.html', {'form': form})

class ConverseCustomizePage(View):
    def get(self, request):
        return render(request, 'Converse/converse_customizer.html')
    
class DesignPage(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'sizes': ['EU 38', 'EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43', 'EU 44'],
            'shoe_parts': [
                {'key': 'upper', 'label': 'Upper', 'default': '#1a7a4a'},
                {'key': 'sole', 'label': 'Sole', 'default': '#333333'},
                {'key': 'lining', 'label': 'Lining', 'default': '#f5f5f5'},
                {'key': 'lace', 'label': 'Laces', 'default': '#1a7a4a'},
                {'key': 'heel', 'label': 'Heel', 'default': '#222222'},
            ],
            'patterns': [
                {'key': 'solid', 'label': 'Solid', 'preview': '#1a7a4a'},
                {'key': 'stripe', 'label': 'Stripes', 'preview': 'repeating-linear-gradient(45deg,#1a7a4a,#1a7a4a 4px,#333 4px,#333 8px)'},
                {'key': 'dot', 'label': 'Dots', 'preview': 'radial-gradient(circle,#1a7a4a 3px,#333 3px)'},
                {'key': 'checker', 'label': 'Checker', 'preview': 'repeating-conic-gradient(#1a7a4a 0% 25%,#333 0% 50%) 0 0 / 12px 12px'},
                {'key': 'chevron', 'label': 'Chevron', 'preview': 'repeating-linear-gradient(135deg,#1a7a4a,#1a7a4a 4px,transparent 4px,transparent 8px)'},
            ],
        }
        return render(request, 'Design/designer.html', context)


def LogoutUser(request):
    logout(request)
    messages.success(request, 'Logout successful..')
    return redirect('account:login')

class SendOTPView(View):
    def get(self, request):
        user_id = request.session.get('pending_user_id')

        if not user_id:
            return redirect('account:register')

        user = CustomUser.objects.filter(id=user_id).first()

        if not user or user.is_email_verified:
            request.session.pop('pending_user_id', None)
            return redirect('account:login')

        return render(request, 'email/verify_email.html', { 'pending_user': user })

    def post(self, request):
        user_id = request.session.get('pending_user_id')

        if not user_id:
            return redirect('account:register')

        user = CustomUser.objects.filter(id=user_id).first()

        if not user or user.is_email_verified:
            request.session.pop('pending_user_id', None)
            return redirect('account:login')

        _, email_sent = create_and_send_otp(user)

        if email_sent:
            messages.success(
                request,
                f"A verification code was sent to {user.email}."
            )
        else:
            messages.error(
                request,
                "Failed to send the verification email. Please try again."
            )

        return render(request, 'email/verify_email.html', { 'pending_user': user })


class VerifyOTPView(View):
    def get(self, request):
        user_id = request.session.get('pending_user_id')

        if not user_id:
            return redirect('account:register')

        user = CustomUser.objects.filter(id=user_id).first()

        if not user:
            request.session.pop('pending_user_id', None)
            return redirect('account:register')

        return render(request, 'email/verify_email.html', { 'pending_user': user })

    def post(self, request):
        user_id = request.session.get('pending_user_id')

        if not user_id:
            return redirect('account:register')

        user = CustomUser.objects.filter(id=user_id).first()

        if not user:
            request.session.pop('pending_user_id', None)
            return redirect('account:register')

        submitted_otp = request.POST.get('otp', '').strip()

        if not submitted_otp or len(submitted_otp) != 6 or not submitted_otp.isdigit():
            messages.error(request, "Please enter a valid 6-digit code.")
            return render(request, 'email/verify_email.html', { 'pending_user': user })

        result = verify_otp(user, submitted_otp)

        if result == 'valid':
            request.session.pop('pending_user_id', None)

            messages.success(
                request,
                'Email verified successfully. Please log in.'
            )
            return redirect('account:login')

        elif result == 'expired':
            messages.error(request, "Your code has expired. Please request a new one.")
        else:
            messages.error(request, "Invalid code. Please try again.")

        return render(request, 'email/verify_email.html', { 'pending_user': user })
    

#add to cart view


@login_required
@require_http_methods(["GET", "POST"])
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
 
        size = data.get('size', '').strip()
        pattern = data.get('pattern', '')
        colors = data.get('colors', {})
 
        if not size:
            return JsonResponse({'error': 'Size is required'}, status=400)
 
        try:
            quantity = int(data.get('quantity', 1))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Quantity must be a number'}, status=400)
 
        if quantity < 1:
            return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)
 
        # TODO: replace with a real price lookup once you have one
        unit_price = 5499
 
        item, created = CartItem.objects.get_or_create(
            user=request.user,
            size=size,
            pattern=pattern,
            colors=colors,
            defaults={'unit_price': unit_price, 'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()
 
        cart_item_count = CartItem.objects.filter(user=request.user).aggregate(
            total=Sum('quantity')
        )['total'] or 0
 
        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'size': item.size,
            'unit_price': str(item.unit_price),
            'quantity': item.quantity,
            'cart_item_count': cart_item_count,
        })
 
    # GET: someone navigating here directly, e.g. from a "Review Order"
    # link on the designer page. Pull the design out of the query string
    # and use it to pre-fill the confirmation page.
    size = request.GET.get('size', '')
    pattern = request.GET.get('pattern', '')
    quantity_raw = request.GET.get('quantity', '1')
 
    try:
        quantity = max(1, int(quantity_raw))
    except (TypeError, ValueError):
        quantity = 1
 
    colors_raw = request.GET.get('colors', '{}')
    try:
        colors = json.loads(colors_raw)
    except json.JSONDecodeError:
        colors = {}
 
    # TODO: replace with a real price lookup once you have one
    unit_price = 5499
    line_total = unit_price * quantity
 
    context = {
        'item_name': 'Custom Shoe',
        'item_size': f'EU {size}' if size else 'EU 44',
        'item_price': unit_price,
        'item_count': quantity,
        'items_total': line_total,
        'subtotal': line_total,
        'total': line_total,
 
        'raw_size': size,
        'raw_pattern': pattern,
        'raw_colors_json': json.dumps(colors),
    }
    return render(request, 'add_to_cart/add_to_cart.html', context)
 
# views.py
@login_required
@require_http_methods(["POST"])
def update_cart_quantity(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if quantity < 1:
        return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.quantity = quantity
    item.save()

    cart_item_count = CartItem.objects.filter(user=request.user).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    return JsonResponse({'cart_item_count': cart_item_count})

# ---------------------------------------------------------------------------
# Add these to your existing views.py (in the same app as add_to_cart).
# Make sure these imports are present at the top of that file:
#
#   import json
#   from django.contrib.auth.decorators import login_required
#   from django.views.decorators.http import require_POST, require_http_methods
#   from django.shortcuts import render, get_object_or_404
#   from django.http import JsonResponse
#   from django.db.models import Sum
#   from .models import CartItem
# ---------------------------------------------------------------------------


@login_required
def view_cart(request):
    """
    Renders the Your Cart page: every CartItem belonging to the logged-in
    user, plus an order summary (subtotal, item count) and a placeholder
    "You May Also Like" list.
    """
    cart_items = CartItem.objects.filter(user=request.user)

    subtotal = sum(item.line_total for item in cart_items)
    cart_item_count = cart_items.aggregate(total=Sum('quantity'))['total'] or 0

    # TODO: replace with a real query once you have a Shoe/Product model,
    # e.g. Shoe.objects.exclude(id__in=[...]).order_by('?')[:4]
    # Hardcoded for now so the page renders end-to-end. Update the image
    # paths to match whatever you actually have under static/images/.
    recommended_products = [
        {'name': 'Classic White', 'price': 4299, 'image': 'images/classic-white.png'},
        {'name': 'All Black', 'price': 4799, 'image': 'images/all-black.png'},
        {'name': 'Navy Breeze', 'price': 4599, 'image': 'images/navy-breeze.png'},
        {'name': 'Beige Minimal', 'price': 4299, 'image': 'images/beige-minimal.png'},
    ]

    return render(request, 'view_cart/view_cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'cart_item_count': cart_item_count,
        'recommended_products': recommended_products,
    })


@login_required
@require_POST
def update_cart_quantity(request):
    """
    Called by cart.js whenever the +/- stepper on a cart card is clicked.
    Updates one CartItem's quantity and returns fresh totals so the page
    can update the numbers without a full reload.
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if quantity < 1:
        return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.quantity = quantity
    item.save()

    remaining = CartItem.objects.filter(user=request.user)
    cart_item_count = remaining.aggregate(total=Sum('quantity'))['total'] or 0
    subtotal = sum(i.line_total for i in remaining)

    return JsonResponse({
        'line_total': str(item.line_total),
        'subtotal': str(subtotal),
        'cart_item_count': cart_item_count,
    })


@login_required
@require_POST
def remove_from_cart(request):
    """
    Called by cart.js when the Remove button on a cart card is clicked.
    Deletes the CartItem and returns fresh totals.
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()

    remaining = CartItem.objects.filter(user=request.user)
    cart_item_count = remaining.aggregate(total=Sum('quantity'))['total'] or 0
    subtotal = sum(i.line_total for i in remaining)

    return JsonResponse({
        'subtotal': str(subtotal),
        'cart_item_count': cart_item_count,
    })


# ---------------------------------------------------------------------------
# Also update your existing add_to_cart view to return the new item's id —
# cart.js and designer.html's script both need it for later quantity syncs.
# In the JsonResponse at the end of add_to_cart, add:
#
#   return JsonResponse({
#       'id': item.id,          # <-- add this line
#       'name': item.name,
#       'size': item.size,
#       'unit_price': str(item.unit_price),
#       'quantity': item.quantity,
#       'cart_item_count': cart_item_count,
#   })
# ---------------------------------------------------------------------------


class ProfileView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request):
        if request.user.is_superuser:
            messages.error(request, "Admins are not allowed to access this page.")
            return redirect('account:login')

        return render(request, 'profile/profile.html')


class UpdateProfileView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(
            request,
            'profile/update_profile.html',
            {'form': form, 'address_fields': ProfileUpdateForm.ADDRESS_FIELD_NAMES},
        )

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('account:profile')

        messages.error(request, "Please correct the errors below.")
        return render(
            request,
            'profile/update_profile.html',
            {'form': form, 'address_fields': ProfileUpdateForm.ADDRESS_FIELD_NAMES},
        )


class DeleteProfileView(LoginRequiredMixin, View):
    login_url = 'account:login'

    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('account:login')
