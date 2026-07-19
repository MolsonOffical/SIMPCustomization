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
	path('cart/', views.CartView.as_view(), name='cart_view'),
	path('history/', views.History.as_view(), name='history'),

]
