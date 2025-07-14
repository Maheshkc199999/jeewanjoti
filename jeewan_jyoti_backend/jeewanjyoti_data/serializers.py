from rest_framework import serializers
from .models.HeartRate import HeartRate_Data
from .models.SPO2 import BloodOxygen
from .models.HRV import HRV
from .models.Toatal_day_activity import activity_day_total
from .models.Steps import StepData
from .models.Sleep import SleepData
from .models.Temperature import BodyTemperature
from .models.battery import BatteryStatus


class HeartRateDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRate_Data
        fields = ['device_id', 'date', 'once_heart_value', 'user']


class HRVDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRV
        fields = ['device_id', 'date', 'highBP', 'lowBP', 'stress', 'heartRate', 'vascularAging', 'hrv', 'user']


class BloodOxygenSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodOxygen
        fields = ['device_id', 'date', 'Blood_oxygen', 'user']


class Total_activity_DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = activity_day_total
        fields = ['device_id', 'date', 'goal', 'distance', 'distance', 'step', 'exercise_time', 'calories',
                  'exercise_minutes', 'user']


class StepDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepData
        fields = ['device_id', 'date', 'detail_minter_step', 'distance', 'calories', 'array_steps', 'user']


class TemperatureDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = BodyTemperature
        fields = ['device_id', 'date', 'axillaryTemperature', 'user']


class SleepDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepData
        fields = ['device_id', 'date', 'start_time', 'end_time', 'duration', 'sleep_quality_sequence',
                  'awake_percentage', 'deep_sleep_percentage', 'light_sleep_percentage', 'medium_sleep_percentage',
                  'user']


class BatteryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryStatus
        fields = ['percentage', 'timestamp', 'device_id', 'user']