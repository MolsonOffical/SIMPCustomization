from django.urls import path
from . import views

app_name = 'shoes'

urlpatterns = [
    path('', views.ShoesListView.as_view(), name='shoes_list'),
    path('<int:pk>/', views.ShoeDetailView.as_view(), name='shoe_detail'),
    path('category/<int:category_id>/', views.ShoesListView.as_view(), name='category'),
    # path('parash/', views.test, name='test'),

    path("cart/", views.cart_page, name="cart_page"),
    path("cart/api/items/", views.cart_item_list, name="cart_item_list"),
    path("cart/api/add/", views.cart_add, name="cart_add"),
    path("cart/api/update/", views.cart_update, name="cart_update"),
    path("cart/api/remove/", views.cart_remove, name="cart_remove"),
    path("cart/api/clear/", views.cart_clear, name="cart_clear"),

    path('history/', views.History.as_view(), name='history'),
]