from django.db import models
from jeewanjyoti_user.models import  CustomUser

class BatteryStatus(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50)
    percentage = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)  # Updates every time the object is saved

    def save(self, *args, **kwargs):
        # Delete all existing records before saving a new one
        BatteryStatus.objects.all().delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.percentage}% at {self.timestamp}"