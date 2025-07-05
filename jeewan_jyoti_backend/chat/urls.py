from django.urls import path
from . import views

urlpatterns = [
    path('history/<int:user_id>/', views.chat_history, name='chat_history'),
    path('send/', views.send_message, name='send_message'),
    path('seen/<int:message_id>/', views.mark_as_seen, name='mark_seen'),
]
