from rest_framework import serializers
from .models import *

class ChatMesageSerilazer(serializers.ModelSerializer):
    class Meta:
        model=UserChatMessage
        fields=["id","user_input","api_response","created_at"]
        read_only_fields=["user_input","api_response","created_at","id"]
        

