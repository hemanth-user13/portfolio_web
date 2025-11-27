from django.contrib import admin
from .models import *

# Register your models here.
class UserChatHistory(admin.ModelAdmin):
    list_display=('user_input','api_response','created_at')

admin.site.register(UserChatMessage, UserChatHistory)
admin.site.register(MyData)