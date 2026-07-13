from django.contrib import admin
from .models import CustomUser, EmailOTP,CartItem
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(EmailOTP)
admin.site.register(CartItem)