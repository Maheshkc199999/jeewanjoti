from django.db import models
from datetime import datetime
from jeewanjyoti_user.models import  CustomUser

class activity_day_total(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50) 
    date = models.DateField(default=datetime.now)
    goal = models.IntegerField()
    distance = models.FloatField()
    step = models.IntegerField()
    exercise_time = models.IntegerField()
    calories = models.FloatField()
    exercise_minutes = models.IntegerField()
    

    def __str__(self):
       return f"{self.device_id} - {self.date} - Goal: {self.goal} - Distance: {self.distance} km - Steps: {self.step} - Exercise Time: {self.exercise_time} mins - Calories: {self.calories} kcal - Exercise Minutes: {self.exercise_minutes}"