from django.urls import path
from . import views

app_name = 'shoes'

urlpatterns = [
    path('', views.ShoesListView.as_view(), name='shoes_list'),
    path('<int:pk>/', views.ShoeDetailView.as_view(), name='shoe_detail'),
    path('category/<int:category_id>/', views.ShoesListView.as_view(), name='category'),
]