from django.db import models
from datetime import datetime
from jeewanjyoti_user.models import  CustomUser

class BodyTemperature(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50) 
    date = models.DateTimeField(default=datetime.now)
    axillaryTemperature = models.FloatField()
    

    def __str__(self):
        return f"{self.device_id} - {self.date} - {self.axillaryTemperature}"