from django.db import models
from datetime import datetime
from jeewanjyoti_user.models import  CustomUser

class HRV(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50) 
    date = models.DateTimeField(default=datetime.now)
    highBP = models.IntegerField()
    lowBP = models.IntegerField()
    stress = models.IntegerField()
    heartRate = models.IntegerField()
    vascularAging = models.IntegerField()
    hrv = models.IntegerField()
    
      

    def __str__(self):
        return f"{self.device_id} - {self.date} - High: {self.highBP} - Low: {self.lowBP} - Stress: {self.stress} - HeartRate: {self.heartRate} - Vascular Aging: {self.vascularAging} -HRV: {self.hrv}"
