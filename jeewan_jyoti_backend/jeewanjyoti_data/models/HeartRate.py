from django.db import models
from datetime import datetime
from jeewanjyoti_user.models import  CustomUser

class HeartRate_Data(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50) 
    date = models.DateTimeField(default=datetime.now)
    once_heart_value = models.IntegerField()
   

    def __str__(self):
        return f"{self.device_id} - {self.date} - {self.once_heart_value}"