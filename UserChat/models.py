from django.db import models

# Create your models here.
class UserChatMessage(models.Model):
    user_input=models.TextField()
    api_response=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat at{self.user_input}"
    

class MyData(models.Model):
    text=models.TextField()
    embedding = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.text[:50]
