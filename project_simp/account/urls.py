from django.urls import path
from .views import (
    HomePage, AboutPage, RegisterUser, LoginUser, LogoutUser,
    SendOTPView, VerifyOTPView, DesignPage,add_to_cart,update_cart_quantity,view_cart,remove_from_cart,
)

app_name = 'account'

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('about/', AboutPage.as_view(), name='about'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser, name='logout'),

    path('verify-email/', SendOTPView.as_view(), name='send_otp'),
    path('verify-email/confirm/', VerifyOTPView.as_view(), name='verify_otp'),
    path('design/', DesignPage.as_view(), name='design'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    # ---------------------------------------------------------------------------
# Add these three paths to your existing urls.py, inside the account app's
# urlpatterns list (same file/app namespace as add_to_cart).
# ---------------------------------------------------------------------------

    path('cart/', view_cart, name='view_cart'),
    path('cart/update-quantity/', update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/',remove_from_cart, name='remove_from_cart'),

# ---------------------------------------------------------------------------
# One more fix needed in designer.html: the "View Cart" link currently
# points at the add-to-cart POST endpoint, which is wrong — it should point
# at the new view_cart page. Change this line:
#
#   <a id="cm-view-cart" href="{% url 'account:add_to_cart' %}" ...>
#
# to:
#
#   <a id="cm-view-cart" href="{% url 'account:view_cart' %}" ...>
# ---------------------------------------------------------------------------

    
]