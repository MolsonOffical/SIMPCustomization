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
from django.contrib.auth.decorators import login_required
from .models import CartItem, PATTERN_PRICES, SIZE_CHOICES
from django.db.models import Sum, Min, F, Avg, Count,Q,OuterRef, Subquery
from shoes.models import Shoes, Category, Brand, Review
from django.db.models import Min, Avg, Count, Sum, OuterRef, Subquery, IntegerField, Value, FloatField
from django.db.models.functions import Coalesce


from shoes.models import OrderItem

class AboutPage(View):
    def get(self, request):
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
                    request.session['pending_user_id'] = user.id
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

class ChooseShoePage(View):
     def get(self, request):
        shoes = (
            Shoes.objects
            .exclude(customizer_id__isnull=True)
            .exclude(customizer_id='')
            .order_by('name')
        )
        return render(request, 'ChooseShoe/choose_shoe.html', {'shoes': shoes})


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


class HomePage(View):
    def get(self, request):
        new_arrivals = Shoes.objects.select_related('category', 'brand').annotate(
            min_price=Min('variants__price'),
            avg_rating=Coalesce(Avg('reviews__rating'), Value(0.0), output_field=FloatField()),
            review_count=Count('reviews', distinct=True),
        ).order_by('-created_at')[:9]

        units_sold_sq = (
            OrderItem.objects
            .filter(
                variant__shoe=OuterRef('pk'),
                order__status__in=['paid', 'processing', 'shipped', 'delivered'],
            )
.values('variant__shoe')
            .annotate(total=Sum('quantity'))
            .values('total')
        )

        popular_shoes = Shoes.objects.select_related('category', 'brand').annotate(
            min_price=Min('variants__price'),
            avg_rating=Coalesce(Avg('reviews__rating'), Value(0.0), output_field=FloatField()),
            review_count=Count('reviews', distinct=True),
            units_sold=Coalesce(
                Subquery(units_sold_sq, output_field=IntegerField()), 0
            ),
        ).filter(review_count__gt=0).order_by('-units_sold', '-avg_rating')[:6]

        categories = Category.objects.all().order_by('name')

        brands = Brand.objects.annotate(shoe_count=Count('shoes')).order_by('-shoe_count')[:4]

        testimonials = Review.objects.exclude(comment='').select_related(
            'user', 'shoe'
        ).order_by('-created_at')[:5]

        top_shoe_per_category = Shoes.objects.filter(
            category=OuterRef('category')
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-review_count', '-avg_rating')

        category_shoes = Shoes.objects.annotate(
            min_price=Min('variants__price')
        ).filter(
            pk__in=Subquery(top_shoe_per_category.values('pk')[:1])
        ).select_related('category').order_by('category__name')[:6]

        context = {
            'new_arrivals': new_arrivals,
            'popular_shoes': popular_shoes,
            'categories': categories,
            'brands': brands,
            'testimonials': testimonials,
            'category_shoes': category_shoes,
        }
        return render(request, 'Home/index.html', context)