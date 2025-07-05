import requests
from rest_framework import serializers
from .models.appointment import Appointment
from .models.location import Location
from django.conf import settings
from django.utils.timezone import now

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['user', 'doctor', 'appointment_date', 'appointment_time', 'is_immediate', 'user_report', 'status', 'problem_description', 'invoice_no','amount']
        read_only_fields = ['invoice_no']

    def validate_appointment_date(self, value):
        if value < now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value
    
    def validate(self, data):
        if data.get('is_immediate') and (data.get('appointment_date') or data.get('appointment_time')):
            raise serializers.ValidationError("Immediate appointments do not require appointment date/time.")
        return data


class KhaltiPaymentSerializer(serializers.Serializer):
    token = serializers.CharField()
    amount = serializers.IntegerField()

    def validate(self, data):
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }
        payload = {
            "token": data["token"],
            "amount": data["amount"]
        }
        response = requests.post(settings.KHALTI_VERIFY_URL, data=payload, headers=headers)

        if response.status_code != 200:
            raise serializers.ValidationError("Payment verification failed.")

        return data
    
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id","user","device_id", "latitude","longitude","locality","city", "state","country","created_at" ]