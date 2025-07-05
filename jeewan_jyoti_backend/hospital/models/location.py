from django.db import models
from jeewanjyoti_user.models import CustomUser

class Location(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='location')
    device_id = models.CharField(max_length=50, blank=True, null=True) 
    latitude = models.FloatField()
    longitude = models.FloatField()
    locality = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.locality}, {self.city}, {self.state}, {self.country}"