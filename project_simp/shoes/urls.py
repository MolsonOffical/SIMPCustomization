from django.urls import path
from . import views

app_name = 'shoes'

urlpatterns = [
    path('', views.ShoesListView.as_view(), name='shoes_list'),
    path('<int:pk>/', views.ShoeDetailView.as_view(), name='shoe_detail'),
    path('<int:pk>/review/', views.AddReviewView.as_view(), name='add_review'),
    path('<int:pk>/review/<int:review_id>/edit/', views.EditReviewView.as_view(), name='edit_review'),
    path('<int:pk>/review/<int:review_id>/delete/', views.DeleteReviewView.as_view(), name='delete_review'),
    path('category/<int:category_id>/', views.ShoesListView.as_view(), name='category'),

    path('parash/', views.test, name='test'),
	
	path('history/', views.order_history_view, name='history'),
    path('orders/<str:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('orders/<str:order_id>/track/', views.order_tracking_view, name='order_tracking_view'),
    path('orders/<str:order_id>/success/', views.payment_success_view, name='payment_success_view'),
    path('orders/create/', views.create_order, name='create_order'),
    path('payments/esewa/initiate/<str:order_id>/', views.esewa_initiate, name='esewa_initiate'),
    path('payments/esewa/verify/<str:order_id>/', views.esewa_verify, name='esewa_verify'),
    path('payments/khalti/initiate/<str:order_id>/', views.khalti_initiate, name='khalti_initiate'),
    path('payments/khalti/verify/<str:order_id>/', views.khalti_verify, name='khalti_verify'),


    path("cart/", views.cart_page, name="cart_page"),
    path("cart/api/items/", views.cart_item_list, name="cart_item_list"),
    path("cart/api/add/", views.cart_add, name="cart_add"),
    path("cart/api/update/", views.cart_update, name="cart_update"),
    path("cart/api/remove/", views.cart_remove, name="cart_remove"),
    path("cart/api/clear/", views.cart_clear, name="cart_clear"),


]