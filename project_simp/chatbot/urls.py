from django.urls import path
from .views import chatbot_mind

urlpatterns=[
    path("",chatbot_mind,name='mind'),
]