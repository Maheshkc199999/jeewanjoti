from django.db import models
from jeewanjyoti_user.models import CustomUser
class ChatMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat/files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message[:20]}"
