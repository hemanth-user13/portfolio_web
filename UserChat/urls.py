from django.urls import path
from .views import *

urlpatterns = [
    path('chat', UserChat.as_view(), name='user-chat-api'),
    path('ask', Ask.as_view(), name='ask_ai'),
]
