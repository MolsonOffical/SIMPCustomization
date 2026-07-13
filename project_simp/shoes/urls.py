from django.urls import path
from . import views

app_name = 'shoes'

urlpatterns = [
    path('', views.ShoesListView.as_view(), name='shoes_list'),
    path('<int:pk>/', views.ShoeDetailView.as_view(), name='shoe_detail'),
    path('category/<int:category_id>/', views.ShoesListView.as_view(), name='category'),
    path('parash/', views.test, name='test'),
	path('cart/', views.CartView.as_view(), name='cart_view'),
	path('history/', views.History.as_view(), name='history'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('orders/<str:order_id>/track/', views.order_tracking_view, name='order_tracking_view'),
    path('orders/create/', views.create_order, name='create_order'),
path('payments/esewa/initiate/<str:order_id>/', views.esewa_initiate, name='esewa_initiate'),
path('payments/esewa/verify/<str:order_id>/', views.esewa_verify, name='esewa_verify'),
path('payments/khalti/initiate/<str:order_id>/', views.khalti_initiate, name='khalti_initiate'),
path('payments/khalti/verify/<str:order_id>/', views.khalti_verify, name='khalti_verify'),

]
