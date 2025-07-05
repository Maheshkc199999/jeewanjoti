from rest_framework.response import Response
from datetime import timedelta
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

from .serializers import HeartRateDataSerializer,HRVDataSerializer,BloodOxygenSerializer,Total_activity_DataSerializer,StepDataSerializer,TemperatureDataSerializers,SleepDataSerializer,BatteryStatusSerializer
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

        # Prepare and bulk insert data
        data_to_insert = [
            HeartRate_Data(
                user=request.user,  # Use object instead of ID to avoid extra lookup
                device_id=device_id,
                date=record['date'],
                once_heart_value=record['once_heart_value']
            ) for record in valid_values
        ]
        HeartRate_Data.objects.bulk_create(data_to_insert, ignore_conflicts=True)

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
    
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def heartrate_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])

        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"latest_hr_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        latest_date = max(values, key=lambda x: x['date'])['date']
        valid_values = [
            record for record in values 
            if cached_lastdate is None or record['date'] > cached_lastdate
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, 
                            status=status.HTTP_200_OK)

        # Prepare the data for saving
        data_to_insert = [
            {
                "user": request.user.id,
                "device_id": device_id,
                "date": record['date'],
                "once_heart_value": record['once_heart_value']
            }
            for record in valid_values
        ]

        serializer = HeartRateDataSerializer(data=data_to_insert, many=True)
        if serializer.is_valid():
            serializer.save()
            
            # Update the cache with the most recent date
            cache.set(cache_key, latest_date, timeout=None)  # No expiration
            return Response({"message": "Data successfully saved"}, 
                            status=status.HTTP_201_CREATED)

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
        queryset = HeartRate_Data.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = HeartRateDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#for HRV data
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
                "highBP": value['highBP'],
                "lowBP": value['lowBP'],
                "stress": value['stress'],
                "heartRate": value['heartRate'],
                "vascularAging": value['vascularAging'],
                "hrv": value['hrv']
            }
            for value in valid_values
        ]

        serializer = HRVDataSerializer(data=data_to_insert, many=True)
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
        queryset = HRV.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = HRVDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#for bloodoxygendata 
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def Spo2_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])
    
        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"latest_Spo2_date_{device_id}"  # Fixed the cache key
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
                "Blood_oxygen": value['Blood_oxygen']
            }
            for value in valid_values
        ]
        
        serializer = BloodOxygenSerializer(data=data_to_insert, many=True)
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
        queryset = BloodOxygen.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = BloodOxygenSerializer(queryset, many=True)
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

        latest_date = max(values, key=lambda x: x['date'])['date']
        valid_values = [
            record for record in values 
            if cached_lastdate is None or record['date'] > cached_lastdate
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, 
                            status=status.HTTP_200_OK)
        
        # Prepare data for bulk insertion
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
            for value in valid_values
        ]

        # Validate and save data
        serializer = Total_activity_DataSerializer(data=data_to_insert, many=True)
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
        queryset = activity_day_total.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = Total_activity_DataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#steps_data  
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def step_data_view(request):
    if request.method == 'POST':
        device_id = request.data.get('device_id')
        values = request.data.get('values', [])
        
        # Validate required fields
        if not device_id or not values:
            return Response({"error": "Device ID and values are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure 'values' is a list of dictionaries
        if not all(isinstance(value, dict) for value in values):
            return Response({"error": "Values must be a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"latest_steps_date_{device_id}"
        cached_lastdate = cache.get(cache_key)

        latest_date = max(values, key=lambda x: x['date'])['date']
        valid_values = [
            record for record in values 
            if cached_lastdate is None or record['date'] > cached_lastdate
        ]

        if not valid_values:
            return Response({"message": "No new data to save."}, 
                            status=status.HTTP_200_OK)

        # Prepare data for bulk insertion
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
            for value in valid_values
        ]
        
        # Validate and save data
        serializer = StepDataSerializer(data=data_to_insert, many=True)
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
        queryset = StepData.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = StepDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#body temperature
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
              "axillaryTemperature": value['axillaryTemperature']
            }
            for value in valid_values
        ]
        
        serializer = TemperatureDataSerializers(data=data_to_insert, many=True)
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
        queryset = BodyTemperature.objects.filter(user=user_id)

        # Apply additional filters
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        serializer = TemperatureDataSerializers(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#sleep Data
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

#battry status
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

#api to fetch latest data in the dashboard

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
    total_steps = StepData.objects.filter(user=user_id, date__gte=today).aggregate(Sum("detail_minter_step"))["detail_minter_step__sum"] or 0
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


#for the average data of those weeks

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
                return list(model.objects.filter(user=user_id, date__gte=start_time).values_list(field, flat=True))
            elif period == 'week':
                return model.objects.filter(user=user_id, date__gte=start_time).extra({'day': "date(date)"}).values('day').annotate(avg_value=Avg(field)).order_by('day')
            elif period == 'month':
                return model.objects.filter(user=user_id, date__gte=start_time).extra({'week': "strftime('%W', date)"}).values('week').annotate(avg_value=Avg(field)).order_by('week')
            elif period == 'year':
                return model.objects.filter(user=user_id, date__gte=start_time).extra({'month': "strftime('%m', date)"}).values('month').annotate(avg_value=Avg(field)).order_by('month')
        except:
            return []
    
    response_data = {
        "once_heart_value": get_aggregated_data(HeartRate_Data, "once_heart_value"),
        "hrv": get_aggregated_data(HRV, "hrv"),
        "stress": get_aggregated_data(HRV, "stress"),
        "highBP": get_aggregated_data(HRV, "highBP"),
        "lowBP": get_aggregated_data(HRV, "lowBP"),
        "Blood_oxygen": get_aggregated_data(BloodOxygen, "Blood_oxygen"),
        "exercise_time": get_aggregated_data(activity_day_total, "exercise_time"),
        "detail_minter_step": get_aggregated_data(StepData, "detail_minter_step"),
        "axillaryTemperature": get_aggregated_data(BodyTemperature, "axillaryTemperature"),
        "sleep_duration": get_aggregated_data(SleepData, "duration"),
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
