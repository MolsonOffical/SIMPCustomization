from django.urls import path
from .views import (
    HomePage, AboutPage, RegisterUser, LoginUser, LogoutUser,
    SendOTPView, VerifyOTPView, DesignPage, ConverseCustomizePage
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
    path('converse-customize/', ConverseCustomizePage.as_view(), name='converse_customize'),
]