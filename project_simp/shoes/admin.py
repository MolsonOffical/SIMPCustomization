from django.contrib import admin
from .models import Category,Brand,Shoes,ShoesColor,ShoesSize,ShoesVariant
# Register your models here.
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Shoes)
admin.site.register(ShoesColor)
admin.site.register(ShoesSize)
admin.site.register(ShoesVariant)