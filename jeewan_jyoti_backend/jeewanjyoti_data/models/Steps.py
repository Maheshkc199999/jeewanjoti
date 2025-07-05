from django.db import models
from datetime import datetime
from jeewanjyoti_user.models import  CustomUser

class StepData(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50) 
    date = models.DateTimeField(default=datetime.now)
    detail_minter_step = models.IntegerField()
    distance = models.FloatField()
    calories = models.FloatField()
    array_steps = models.TextField() 
  
    
    def __str__(self):
        return f"{self.device_id} - {self.date} - {self.detail_minter_step} - {self.distance} - {self.calories} - {self.array_steps}"
