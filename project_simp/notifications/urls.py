from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('unread-count/', views.UnreadCountView.as_view(), name='unread_count'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),

    path('<int:pk>/', views.NotificationDetailView.as_view(), name='detail'),
    path('<int:pk>/mark-read/', views.MarkAsReadView.as_view(), name='mark_read'),
    path('<int:pk>/toggle-read/', views.ToggleReadView.as_view(), name='toggle_read'),
    path('<int:pk>/delete/', views.DeleteNotificationView.as_view(), name='delete'),
]
