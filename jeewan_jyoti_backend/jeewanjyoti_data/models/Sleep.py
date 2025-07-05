from django.db import models
from datetime import datetime
from jeewanjyoti_user.models import CustomUser

class SleepData(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50)
    date = models.DateTimeField(default=datetime.now)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.FloatField()
    sleep_quality_sequence = models.TextField()
    awake_percentage = models.FloatField()
    deep_sleep_percentage = models.FloatField()
    light_sleep_percentage = models.FloatField()
    medium_sleep_percentage = models.FloatField()

    def __str__(self):
        return f"{self.device_id} - {self.date} - {self.sleep_quality_sequence}"