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
from .models import CartItem, PATTERN_PRICES, SIZE_CHOICES
import base64
from django.core.files.base import ContentFile
# Matches the prices set in shoeColorConfigs in converse_customizer.html.
# Keep these two in sync until you have a real Shoe/Product model with price.


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



VALID_SIZES = {choice[0] for choice in SIZE_CHOICES}


def _cart_item_count(user):
    return CartItem.objects.filter(user=user).count()


@login_required
@require_http_methods(['GET', 'POST'])
def add_to_cart(request):
    """
    POST (AJAX/JSON — customizer's "Add to Cart" button):
        body: {"pattern": "...", "size": "...", "colors": {...}, "quantity": 1}
        -> {"id": <cart_item_id>, "cart_item_count": <int>}

    GET (customizer's "Buy Now" — plain navigation, query params):
        ?pattern=...&size=...&colors=<json string>&quantity=1
        -> saves/updates the item, then redirects to the cart page
    """
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Malformed request body.'}, status=400)
        pattern = payload.get('pattern')
        size = str(payload.get('size', ''))
        colors = payload.get('colors', {})
        quantity = payload.get('quantity', 1)
        photo_data_url = payload.get('photo') 
    else:
        pattern = request.GET.get('pattern')
        size = request.GET.get('size', '')
        try:
            colors = json.loads(request.GET.get('colors', '{}'))
        except json.JSONDecodeError:
            colors = {}
        quantity = request.GET.get('quantity', 1)
        photo_data_url = None   

    try:
        quantity = max(1, min(int(quantity), 10))
    except (TypeError, ValueError):
        quantity = 1

    if pattern not in PATTERN_PRICES:
        error = 'Please choose a valid shoe pattern.'
        if request.method == 'POST':
            return JsonResponse({'error': error}, status=400)
        messages.error(request, error)
        return redirect(request.META.get('HTTP_REFERER', 'account:cart_view'))

    if size not in VALID_SIZES:
        error = 'Please select a size first.'
        if request.method == 'POST':
            return JsonResponse({'error': error}, status=400)
        messages.error(request, error)
        return redirect(request.META.get('HTTP_REFERER', 'account:cart_view'))

    if not isinstance(colors, dict):
        colors = {}

    # Same user + pattern + size + colors already in cart -> bump quantity
    # instead of creating a duplicate row.
    existing = CartItem.objects.filter(
        user=request.user, pattern=pattern, size=size, colors=colors,
    ).first()

    if existing:
        existing.quantity = max(1, min(existing.quantity + quantity, 10))
        existing.save()
        item = existing
    else:
        item = CartItem.objects.create(
            user=request.user, pattern=pattern, size=size,
            colors=colors, quantity=quantity,
        )
        photo_file = _decode_photo(photo_data_url, pattern)   # NEW
        if photo_file:
            item.photo.save(photo_file.name, photo_file, save=True)

    if request.method == 'POST':
        return JsonResponse({
            'id': item.id,
            'cart_item_count': _cart_item_count(request.user),
        })

    return redirect('account:cart_view')


@login_required
@require_http_methods(['POST'])
def update_cart_quantity(request):
    """
    POST (AJAX/JSON): body: {"item_id": <id>, "quantity": <int>}
    Called once "Add to Cart" has flipped to "Update Cart" so repeat
    clicks patch the existing row instead of creating a new one.
    """
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Malformed request body.'}, status=400)

    item = get_object_or_404(CartItem, id=payload.get('item_id'), user=request.user)

    try:
        quantity = max(1, min(int(payload.get('quantity', 1)), 10))
    except (TypeError, ValueError):
        quantity = 1

    item.quantity = quantity
    item.save()

    return JsonResponse({
        'id': item.id,
        'cart_item_count': _cart_item_count(request.user),
    })


@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal for item in items)
    return render(request, 'cart/cart.html', {'items': items, 'total': total})


@login_required
@require_http_methods(['POST'])
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_item_count': _cart_item_count(request.user)})
    return redirect('account:cart_view')




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



def _decode_photo(data_url, pattern):
    """Convert a 'data:image/png;base64,...' string into a Django File."""
    if not data_url or ';base64,' not in data_url:
        return None
    header, encoded = data_url.split(';base64,', 1)
    ext = header.split('/')[-1]  # e.g. 'png'
    try:
        decoded = base64.b64decode(encoded)
    except (TypeError, ValueError):
        return None
    return ContentFile(decoded, name=f'{pattern}-{quantity if False else "snapshot"}.{ext}')