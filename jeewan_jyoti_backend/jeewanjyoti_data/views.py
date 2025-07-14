from rest_framework.response import Response
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models.HeartRate import HeartRate_Data
from .models.SPO2 import BloodOxygen
from .models.HRV import HRV
from .models.Toatal_day_activity import activity_day_total
from .models.Steps import StepData
from .models.Sleep import SleepData
from .models.Temperature import BodyTemperature
from .models.battery import BatteryStatus
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.db.models import Sum
from django.db.models import Avg
import openai
from openai import OpenAI

from .serializers import HeartRateDataSerializer, HRVDataSerializer, BloodOxygenSerializer, \
    Total_activity_DataSerializer, StepDataSerializer, TemperatureDataSerializers, SleepDataSerializer, \
    BatteryStatusSerializer


# heartrate data
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def heartrate_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_hr_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        # Extract dates & filter only new data
        valid_values = [record for record in values if cached_lastdate is None or record['date'] > cached_lastdate]

        if not valid_values:
            return Response({"message": "No new data to save."}, status=status.HTTP_200_OK)

        # Fetch existing dates for the user to avoid duplicates
        existing_dates = set(
            HeartRate_Data.objects.filter(user=request.user, date__in=[v['date'] for v in valid_values])
            .values_list('date', flat=True)
        )

        # Prepare only unique data for insertion
        data_to_insert = [
            HeartRate_Data(
                user=request.user,  # Use object instead of ID to avoid extra lookup
                device_id=device_id,
                date=record['date'],
                once_heart_value=record['once_heart_value']
            ) for record in valid_values if record['date'] not in existing_dates
        ]

        if not data_to_insert:
            return Response({"message": "No new unique data to save."}, status=status.HTTP_200_OK)

        HeartRate_Data.objects.bulk_create(data_to_insert)

        # Update cache with latest date
        latest_date = max(valid_values, key=lambda x: x['date'])['date']
        cache.set(cache_key, latest_date, timeout=None)

        return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        filters = {"user_id": user_id}
        if device_id:
            filters["device_id"] = device_id
        if from_date and to_date:
            filters["date__range"] = (from_date, to_date)
        elif from_date:
            filters["date__gte"] = from_date
        elif to_date:
            filters["date__lte"] = to_date

        queryset = HeartRate_Data.objects.filter(**filters)
        serializer = HeartRateDataSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# for HRV data
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def HRV_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_HRV_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        # Filter out values based on cache
        valid_values = [
            record for record in values
            if isinstance(record, dict) and 'date' in record and
               (cached_lastdate is None or record['date'] > cached_lastdate)
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, status=status.HTTP_200_OK)

        # Check for existing dates to avoid duplicates
        existing_dates = set(
            HRV.objects.filter(user=request.user, date__in=[v['date'] for v in valid_values])
            .values_list('date', flat=True)
        )

        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": value['date'],
                "highBP": value['highBP'],
                "lowBP": value['lowBP'],
                "stress": value['stress'],
                "heartRate": value['heartRate'],
                "vascularAging": value['vascularAging'],
                "hrv": value['hrv']
            }
            for value in valid_values if value['date'] not in existing_dates
        ]

        if not data_to_insert:
            return Response({"message": "No new unique data to save."}, status=status.HTTP_200_OK)

        # Save the data
        serializer = HRVDataSerializer(data=data_to_insert, many=True)
        if serializer.is_valid():
            serializer.save()

            # Update cache with latest date
            latest_date = max(valid_values, key=lambda x: x['date'])['date']
            cache.set(cache_key, latest_date, timeout=None)

            return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        filters = {"user_id": user_id}
        if device_id:
            filters["device_id"] = device_id
        if from_date and to_date:
            filters["date__range"] = (from_date, to_date)
        elif from_date:
            filters["date__gte"] = from_date
        elif to_date:
            filters["date__lte"] = to_date

        queryset = HRV.objects.filter(**filters).order_by("date")
        serializer = HRVDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# for bloodoxygendata
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def Spo2_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_Spo2_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        # Filter out only new data based on cache
        valid_values = [
            record for record in values
            if isinstance(record, dict) and 'date' in record and
               (cached_lastdate is None or record['date'] > cached_lastdate)
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, status=status.HTTP_200_OK)

        # Avoid duplicates: check if same dates already exist in DB
        existing_dates = set(
            BloodOxygen.objects.filter(user=request.user, date__in=[v['date'] for v in valid_values])
            .values_list('date', flat=True)
        )

        # Only insert data not already saved (no duplicate dates)
        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": value['date'],
                "Blood_oxygen": value['Blood_oxygen']
            }
            for value in valid_values if value['date'] not in existing_dates
        ]

        if not data_to_insert:
            return Response({"message": "No new unique data to save."}, status=status.HTTP_200_OK)

        serializer = BloodOxygenSerializer(data=data_to_insert, many=True)
        if serializer.is_valid():
            serializer.save()

            # Update cache with latest date
            latest_date = max(valid_values, key=lambda x: x['date'])['date']
            cache.set(cache_key, latest_date, timeout=None)

            return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        filters = {"user_id": user_id}
        if device_id:
            filters["device_id"] = device_id
        if from_date and to_date:
            filters["date__range"] = (from_date, to_date)
        elif from_date:
            filters["date__gte"] = from_date
        elif to_date:
            filters["date__lte"] = to_date

        queryset = BloodOxygen.objects.filter(**filters).order_by("date")
        serializer = BloodOxygenSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)


# for Day_total_activity
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def Activity_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        # Validate required fields
        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_DTA_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        # Filter only new values
        valid_values = [
            record for record in values
            if isinstance(record, dict) and 'date' in record and
               (cached_lastdate is None or record['date'] > cached_lastdate)
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, status=status.HTTP_200_OK)

        # Get existing dates for the user to avoid duplicates
        existing_dates = set(
            activity_day_total.objects.filter(user=request.user, date__in=[v['date'] for v in valid_values])
            .values_list('date', flat=True)
        )

        # Filter out duplicate dates
        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": value['date'],
                "goal": value['goal'],
                "distance": value['distance'],
                "step": value['step'],
                "exercise_time": value['exercise_time'],
                "calories": value['calories'],
                "exercise_minutes": value['exercise_minutes'],
            }
            for value in valid_values if value['date'] not in existing_dates
        ]

        if not data_to_insert:
            return Response({"message": "No new unique data to save."}, status=status.HTTP_200_OK)

        # Validate and save data
        serializer = Total_activity_DataSerializer(data=data_to_insert, many=True)
        if serializer.is_valid():
            serializer.save()

            # Update cache with latest date
            latest_date = max(valid_values, key=lambda x: x['date'])['date']
            cache.set(cache_key, latest_date, timeout=None)

            return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        filters = {"user_id": user_id}
        if device_id:
            filters["device_id"] = device_id
        if from_date and to_date:
            filters["date__range"] = (from_date, to_date)
        elif from_date:
            filters["date__gte"] = from_date
        elif to_date:
            filters["date__lte"] = to_date

        queryset = activity_day_total.objects.filter(**filters).order_by("date")
        serializer = Total_activity_DataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# steps_data
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def step_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not all(isinstance(value, dict) for value in values):
            return Response({"error": "Values must be a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_steps_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        # Filter values based on cache
        valid_values = [
            record for record in values
            if isinstance(record, dict) and 'date' in record and
               (cached_lastdate is None or record['date'] > cached_lastdate)
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, status=status.HTTP_200_OK)

        # Remove duplicates based on existing DB dates
        existing_dates = set(
            StepData.objects.filter(user=request.user, date__in=[v['date'] for v in valid_values])
            .values_list('date', flat=True)
        )

        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": value['date'],
                "detail_minter_step": value['detail_minter_step'],
                "distance": value['distance'],
                "calories": value['calories'],
                "array_steps": value['array_steps'],
            }
            for value in valid_values if value['date'] not in existing_dates
        ]

        if not data_to_insert:
            return Response({"message": "No new unique data to save."}, status=status.HTTP_200_OK)

        serializer = StepDataSerializer(data=data_to_insert, many=True)
        if serializer.is_valid():
            serializer.save()
            latest_date = max(valid_values, key=lambda x: x['date'])['date']
            cache.set(cache_key, latest_date, timeout=None)
            return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = StepData.objects.filter(user=user_id)

        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = StepDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# body temperature
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def Temperature_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_Temp_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        # Filter values based on cache (date must be newer)
        valid_values = [
            record for record in values
            if isinstance(record, dict) and 'date' in record and
               (cached_lastdate is None or record['date'] > cached_lastdate)
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, status=status.HTTP_200_OK)

        # Remove duplicates based on DB
        existing_dates = set(
            BodyTemperature.objects.filter(user=request.user, date__in=[v['date'] for v in valid_values])
            .values_list('date', flat=True)
        )

        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": value['date'],
                "axillaryTemperature": value['axillaryTemperature']
            }
            for value in valid_values if value['date'] not in existing_dates
        ]

        if not data_to_insert:
            return Response({"message": "No new unique data to save."}, status=status.HTTP_200_OK)

        serializer = TemperatureDataSerializers(data=data_to_insert, many=True)
        if serializer.is_valid():
            serializer.save()
            latest_date = max(valid_values, key=lambda x: x['date'])['date']
            cache.set(cache_key, latest_date, timeout=None)
            return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = BodyTemperature.objects.filter(user=user_id)

        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = TemperatureDataSerializers(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# sleep Data
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def sleep_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_Sleep_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        latest_date = max(values, key=lambda x: x['date'])['date']
        valid_values = [
            record for record in values
            if cached_lastdate is None or record['date'] > cached_lastdate
        ]

        if not valid_values:
            return Response({"message": "No new data to save."},
                            status=status.HTTP_200_OK)

        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": value['date'],
                "start_time": value['start_time'],
                "end_time": value['end_time'],
                "duration": value['duration'],
                "sleep_quality_sequence": value['sleep_quality_sequence'],
                "awake_percentage": value['awake_percentage'],
                "deep_sleep_percentage": value['deep_sleep_percentage'],
                "light_sleep_percentage": value['light_sleep_percentage'],
                "medium_sleep_percentage": value['medium_sleep_percentage']
            }
            for value in valid_values
        ]

        serializer = SleepDataSerializer(data=data_to_insert, many=True)

        if serializer.is_valid():
            serializer.save()
            cache.set(cache_key, latest_date, timeout=None)
            return Response({"message": "Data successfully saved"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        device_id = request.query_params.get('device_id')

        # Ensure user_id is provided
        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch data for the specified user_id
        queryset = SleepData.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = SleepDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# battry status
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def battery_status(request):
    if request.method == 'POST':
        # Automatically set the user to the authenticated user
        request.data['user'] = request.user.id

        serializer = BatteryStatusSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure percentage is within a valid range
            percentage = serializer.validated_data.get('percentage')
            if percentage < 0 or percentage > 100:
                return Response({"error": "Percentage must be between 0 and 100."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()  # This will delete old records and save the new one
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the most recent BatteryStatus object for the specified user
    elif request.method == 'GET':
        # Fetch user_id from query parameters
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the most recent BatteryStatus object for the specified user
        recent_status = BatteryStatus.objects.filter(user_id=user_id).last()

        if recent_status:
            serializer = BatteryStatusSerializer(recent_status)
            return Response(serializer.data)
        else:
            return Response({"error": "No battery status found for this user."}, status=status.HTTP_404_NOT_FOUND)


# api to fetch latest data in the dashboard

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def fetch_latest_single_column_data(request):
    user_id = request.query_params.get('user_id')

    if not user_id:
        user_id = request.user.id
    else:
        user_id = int(user_id)
        if not request.user.is_superuser:
            return Response({"error": "Permission denied. Only superusers can access other users' data."},
                            status=status.HTTP_403_FORBIDDEN)

    def get_latest_value(model, field):
        try:
            return getattr(model.objects.filter(user=user_id).latest('date'), field, "N/A")
        except (ObjectDoesNotExist, AttributeError):
            return "N/A"

    # Get today's date (starting from 12 AM)
    today = now().date()

    # Sum the detail_minter_step from today's records
    total_steps = StepData.objects.filter(user=user_id, date__gte=today).aggregate(Sum("detail_minter_step"))[
                      "detail_minter_step__sum"] or 0
    response_data = {
        "once_heart_value": get_latest_value(HeartRate_Data, "once_heart_value"),
        "hrv": get_latest_value(HRV, "hrv"),
        "stress": get_latest_value(HRV, "stress"),
        "highBP": get_latest_value(HRV, "highBP"),
        "lowBP": get_latest_value(HRV, "lowBP"),
        "Blood_oxygen": get_latest_value(BloodOxygen, "Blood_oxygen"),
        "exercise_time": get_latest_value(activity_day_total, "exercise_time"),
        "detail_minter_step": total_steps,
        "axillaryTemperature": get_latest_value(BodyTemperature, "axillaryTemperature"),
        "sleep_duration": get_latest_value(SleepData, "duration"),
    }

    return Response(response_data, status=status.HTTP_200_OK)


# for the average data of those weeks

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def fetch_aggregated_data(request):
    user_id = request.query_params.get('user_id')
    period = request.query_params.get('period', 'day')  # Default to 'day'

    if not user_id:
        user_id = request.user.id
    else:
        user_id = int(user_id)
        if not request.user.is_superuser:
            return Response({"error": "Permission denied. Only superusers can access other users' data."},
                            status=status.HTTP_403_FORBIDDEN)

    end_time = now()

    if period == 'day':
        start_time = end_time - timedelta(days=1)
    elif period == 'week':
        start_time = end_time - timedelta(days=7)
    elif period == 'month':
        start_time = end_time - timedelta(weeks=4)
    elif period == 'year':
        start_time = end_time - timedelta(weeks=52)
    else:
        return Response({"error": "Invalid period. Choose from: day, week, month, year."},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_aggregated_data(model, field):
        try:
            if period == 'day':
                # For day: return all data points with date and value (last 24 hours)
                query = model.objects.filter(user=user_id, date__gte=start_time)
                if not query.exists():
                    return None
                return [
                    {
                        "date": item.date.isoformat(),
                        "value": getattr(item, field)
                    }
                    for item in query.order_by('date')
                ]
            else:
                # For week, month, year: return aggregated data by date (all available data)
                # Get all data for the user, not limited by start_time for these periods
                all_query = model.objects.filter(user=user_id)
                if not all_query.exists():
                    return None

                # Group by date (from 12:00 AM to 11:59 PM) and calculate daily averages
                aggregated = all_query.annotate(
                    date_only=TruncDate('date')
                ).values('date_only').annotate(
                    avg_value=Avg(field)
                ).order_by('-date_only')  # Most recent first

                # Limit results based on period for better performance
                if period == 'week':
                    aggregated = aggregated[:7]  # Last 7 days
                elif period == 'month':
                    aggregated = aggregated[:30]  # Last 30 days
                elif period == 'year':
                    aggregated = aggregated[:365]  # Last 365 days

                return [
                    {
                        "date": item['date_only'].isoformat(),
                        "value": round(item['avg_value'], 2) if item['avg_value'] else 0
                    }
                    for item in aggregated
                ]
        except Exception as e:
            print(f"Error in get_aggregated_data: {e}")  # Debug print
            return None

    # Get data for all metrics
    heart_rate_data = get_aggregated_data(HeartRate_Data, "once_heart_value")
    hrv_data = get_aggregated_data(HRV, "hrv")
    stress_data = get_aggregated_data(HRV, "stress")
    high_bp_data = get_aggregated_data(HRV, "highBP")
    low_bp_data = get_aggregated_data(HRV, "lowBP")
    blood_oxygen_data = get_aggregated_data(BloodOxygen, "Blood_oxygen")
    exercise_minutes_data = get_aggregated_data(activity_day_total, "exercise_minutes")
    steps_data = get_aggregated_data(StepData, "detail_minter_step")
    temperature_data = get_aggregated_data(BodyTemperature, "axillaryTemperature")
    sleep_duration_data = get_aggregated_data(SleepData, "duration")

    # Build response with only non-null data
    response_data = {}

    if heart_rate_data:
        response_data["once_heart_value"] = heart_rate_data
    if hrv_data:
        response_data["hrv"] = hrv_data
    if stress_data:
        response_data["stress"] = stress_data
    if high_bp_data:
        response_data["highBP"] = high_bp_data
    if low_bp_data:
        response_data["lowBP"] = low_bp_data
    if blood_oxygen_data:
        response_data["Blood_oxygen"] = blood_oxygen_data
    if exercise_minutes_data:
        response_data["exercise_minutes"] = exercise_minutes_data
    if steps_data:
        response_data["detail_minter_step"] = steps_data
    if temperature_data:
        response_data["axillaryTemperature"] = temperature_data
    if sleep_duration_data:
        response_data["sleep_duration"] = sleep_duration_data

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def fetch_daily_data(request):
    user_id = request.query_params.get('user_id')
    date_str = request.query_params.get('date')  # Expecting 'YYYY-MM-DD'
    field = request.query_params.get('field')

    allowed_fields = [
        'heart_rate_data',
        'hrv_data',
        'blood_oxygen_data',
        'activity_data',
        'temperature_data',
        'steps_data',
        'sleep_data'
    ]

    # ✅ Check authentication and permissions
    if not user_id:
        user_id = request.user.id
    else:
        user_id = int(user_id)
        if not request.user.is_superuser:
            return Response({"error": "Permission denied. Only superusers can access other users' data."},
                            status=status.HTTP_403_FORBIDDEN)

    # ✅ Validate date
    if not date_str:
        return Response({"error": "Date parameter is required (format: YYYY-MM-DD)"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        start_time = datetime.strptime(date_str, '%Y-%m-%d')
        end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST)

    # ✅ Validate 'field' param
    if not field:
        return Response({"error": "The 'field' parameter is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    if field not in allowed_fields:
        return Response({"error": f"Invalid field '{field}'. Allowed values: {', '.join(allowed_fields)}."},
                        status=status.HTTP_400_BAD_REQUEST)

    # ✅ Helper to fetch data for the day
    def get_day_data(model, serializer_class):
        try:
            query = model.objects.filter(user=user_id, date__range=(start_time, end_time)).order_by('date')
            if not query.exists():
                return None
            serialized = serializer_class(query, many=True).data
            for item in serialized:
                item.pop('device_id', None)
            return serialized
        except Exception as e:
            print(f"Error in get_day_data: {e}")
            return None

    # ✅ Fetch only the requested dataset
    response_data = {}

    if field == 'heart_rate_data':
        data = get_day_data(HeartRate_Data, HeartRateDataSerializer)
        if data:
            response_data['heart_rate_data'] = data

    elif field == 'hrv_data':
        data = get_day_data(HRV, HRVDataSerializer)
        if data:
            response_data['hrv_data'] = data

    elif field == 'blood_oxygen_data':
        data = get_day_data(BloodOxygen, BloodOxygenSerializer)
        if data:
            response_data['blood_oxygen_data'] = data

    elif field == 'activity_data':
        data = get_day_data(activity_day_total, Total_activity_DataSerializer)
        if data:
            response_data['activity_data'] = data

    elif field == 'temperature_data':
        data = get_day_data(BodyTemperature, TemperatureDataSerializers)
        if data:
            response_data['temperature_data'] = data

    elif field == 'steps_data':
        data = get_day_data(StepData, StepDataSerializer)
        if data:
            response_data['steps_data'] = data

    elif field == 'sleep_data':
        data = get_day_data(SleepData, SleepDataSerializer)
        if data:
            response_data['sleep_data'] = data

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def fetch_AI_data(request):
    user_id = request.user.id

    date_str = request.query_params.get('date')  # Optional
    field = request.query_params.get('field')

    allowed_fields = [
        'heart_rate_data',
        'hrv_data',
        'blood_oxygen_data',
        'activity_data',
        'temperature_data',
        'steps_data',
        'sleep_data'
    ]

    if not field:
        return Response({"error": "The 'field' parameter is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    if field not in allowed_fields:
        return Response({"error": f"Invalid field '{field}'. Allowed values: {', '.join(allowed_fields)}."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Determine date range
    if date_str:
        try:
            start_time = datetime.strptime(date_str, '%Y-%m-%d')
            end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

    # Helper to fetch data
    def get_day_data(model, serializer_class):
        query = model.objects.filter(user=user_id, date__range=(start_time, end_time)).order_by('date')
        if not query.exists():
            return []
        return serializer_class(query, many=True).data

    # Fetch the requested field data
    raw_data = []

    if field == 'heart_rate_data':
        raw_data = get_day_data(HeartRate_Data, HeartRateDataSerializer)

    elif field == 'blood_oxygen_data':
        raw_data = get_day_data(BloodOxygen, BloodOxygenSerializer)

    elif field == 'temperature_data':
        raw_data = get_day_data(BodyTemperature, TemperatureDataSerializers)

    elif field == 'steps_data':
        raw_data = get_day_data(StepData, StepDataSerializer)

    elif field == 'activity_data':
        raw_data = get_day_data(activity_day_total, Total_activity_DataSerializer)

    elif field == 'hrv_data':
        raw_data = get_day_data(HRV, HRVDataSerializer)

    elif field == 'sleep_data':
        raw_data = get_day_data(SleepData, SleepDataSerializer)

    if not raw_data:
        return Response({"error": f"No data found for {field} on {start_time.strftime('%Y-%m-%d')}."},
                        status=status.HTTP_404_NOT_FOUND)

    # ✅ Prepare prompt for DeepSeek
    prompt = f"""
    I have the following user health data for the field '{field}' on {start_time.strftime('%Y-%m-%d')}:

    {raw_data}

    Please analyze it and provide:
    - A short health summary
    - 2-3 clear health recommendations to improve or maintain good health

    Format your response strictly as:
    SUMMARY: <your summary here>
    RECOMMENDATIONS:
    1. <recommendation 1>
    2. <recommendation 2>
    3. <recommendation 3>
    """

    # ✅ Call DeepSeek API through OpenRouter
    try:
        # Initialize OpenAI client with OpenRouter configuration
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )

        # Make the API call
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional: Replace with your site URL
                "X-Title": "<YOUR_SITE_NAME>",  # Optional: Replace with your site name
            },
            extra_body={},
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": "You are a health assistant that gives concise and helpful feedback."},
                {"role": "user", "content": prompt}
            ]
        )

        ai_text = completion.choices[0].message.content

        # ✅ Parse AI response
        summary = ""
        recommendations = []

        if "SUMMARY:" in ai_text and "RECOMMENDATIONS:" in ai_text:
            summary_part, recommendations_part = ai_text.split("RECOMMENDATIONS:")
            summary = summary_part.replace("SUMMARY:", "").strip()
            recommendations = [line.strip().split(". ", 1)[-1] for line in recommendations_part.strip().split("\n") if
                               line.strip()]
        else:
            summary = ai_text.strip()
            recommendations = []

    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return Response({"error": "Failed to generate AI summary."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ✅ Final response
    return Response({
        "date": start_time.strftime('%Y-%m-%d'),
        "field": field,
        "summary": summary,
        "recommendations": recommendations
    }, status=status.HTTP_200_OK)