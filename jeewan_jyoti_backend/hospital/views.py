import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models.appointment import Appointment
from .models.location import Location
from .serializers import AppointmentSerializer, LocationSerializer
from jeewanjyoti_user.models import CustomUser


# @api_view(['POST', 'GET'])
# @permission_classes([IsAuthenticated])  
# @authentication_classes([JWTAuthentication])  
# def book_appointment(request):
#     if request.method == 'POST':
#         # Get data from request
#         doctor_id = request.data.get('doctor_id')
#         is_immediate = request.data.get('is_immediate', False)
        
#         if not doctor_id:
#             return Response({"detail": "Doctor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate if the doctor exists and has the role 'DOCTOR'
#         try:
#             doctor = CustomUser.objects.get(id=doctor_id, role='DOCTOR')
#         except CustomUser.DoesNotExist:
#             return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         appointment_data = request.data.copy()
#         appointment_data['user'] = request.user.id  
#         appointment_data['doctor'] = doctor.id 

#         if is_immediate:
#             appointment_data.pop('appointment_date', None)
#             appointment_data.pop('appointment_time', None)
#             appointment_data['status'] = 'CONFIRMED'

#         serializer = AppointmentSerializer(data=appointment_data)
#         if serializer.is_valid():
#             appointment = serializer.save()

#             # Prepare the response data
#             response_data = {
#                 "appointment_id": appointment.id,
#                 "invoice_no": appointment.invoice_no,
#                 "user_name": f"{appointment.user.first_name} {appointment.user.last_name}",
#                 "doctor_name": f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}",
#                 "status": appointment.status,
#                 "problem_description": appointment.problem_description,
#                 "created_at": appointment.created_at
#             }

#             if not is_immediate:
#                 response_data["appointment_date"] = appointment.appointment_date
#                 response_data["appointment_time"] = appointment.appointment_time

#             return Response(response_data, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'GET':
#         appointments = Appointment.objects.filter(user=request.user)
#         serializer = AppointmentSerializer(appointments, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
# def initiate_payment(request):
#     """
#     Initiates Khalti ePayment and returns the payment URL.
#     """
#     user = request.user
#     amount = request.data.get('amount', None)
#     doctor_id = request.data.get('doctor_id')

#     if not amount or not doctor_id:
#         return Response({"detail": "Amount and Doctor ID are required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Check if doctor exists
#     try:
#         doctor = CustomUser.objects.get(id=doctor_id, role='DOCTOR')
#     except CustomUser.DoesNotExist:
#         return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

#     # Khalti API request payload
#     payload = {
#         "return_url": "https://your-website.com/payment-success/",
#         "website_url": "https://your-website.com/",
#         "amount": amount,  # Khalti amount must be in paisa (e.g., 1300 = 13.00 NPR)
#         "purchase_order_id": f"apt_{user.id}_{doctor.id}",
#         "purchase_order_name": "Appointment Booking",
#         "customer_info": {
#             "name": f"{user.first_name} {user.last_name}",
#             "email": user.email,
#             "phone": user.profile.phone if hasattr(user, 'profile') else "N/A"
#         },
#         "amount_breakdown": [
#             {"label": "Consultation Fee", "amount": amount}
#         ],
#         "product_details": [
#             {
#                 "identity": f"appointment_{user.id}_{doctor.id}",
#                 "name": "Doctor Consultation",
#                 "total_price": amount,
#                 "quantity": 1,
#                 "unit_price": amount
#             }
#         ]
#     }

#     headers = {
#         "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(settings.KHALTI_INITIATE_URL, json=payload, headers=headers)

#     if response.status_code == 200:
#         data = response.json()
#         return Response({
#             "payment_url": data["payment_url"],
#             "pidx": data["pidx"]
#         }, status=status.HTTP_200_OK)
    
#     return Response({"detail": "Failed to initiate payment."}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST', 'GET'])
# @permission_classes([IsAuthenticated])  
# @authentication_classes([JWTAuthentication])  
# def book_appointment(request):
#     if request.method == 'POST':
#         doctor_id = request.data.get('doctor_id')
#         is_immediate = request.data.get('is_immediate', False)
#         pidx = request.data.get('pidx', None)  # Store Khalti transaction ID

#         if not doctor_id:
#             return Response({"detail": "Doctor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             doctor = CustomUser.objects.get(id=doctor_id, role='DOCTOR')
#         except CustomUser.DoesNotExist:
#             return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         appointment_data = request.data.copy()
#         appointment_data['user'] = request.user.id  
#         appointment_data['doctor'] = doctor.id 

#         if is_immediate:
#             appointment_data.pop('appointment_date', None)
#             appointment_data.pop('appointment_time', None)
#             appointment_data['status'] = 'CONFIRMED'

#         if pidx:
#             appointment_data['status'] = 'PENDING_PAYMENT'

#         serializer = AppointmentSerializer(data=appointment_data)
#         if serializer.is_valid():
#             appointment = serializer.save()

#             response_data = {
#                 "appointment_id": appointment.id,
#                 "invoice_no": appointment.invoice_no,
#                 "user_name": f"{appointment.user.first_name} {appointment.user.last_name}",
#                 "doctor_name": f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}",
#                 "status": appointment.status,
#                 "problem_description": appointment.problem_description,
#                 "created_at": appointment.created_at,
#                 "is_paid": appointment.is_paid,
#                 "pidx": pidx  # Return PIDX to track payment
#             }

#             return Response(response_data, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'GET':
#         appointments = Appointment.objects.filter(user=request.user)
#         serializer = AppointmentSerializer(appointments, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
# def verify_payment(request):
#     """
#     Verifies Khalti payment using PIDX.
#     """
#     pidx = request.data.get('pidx', None)

#     if not pidx:
#         return Response({"detail": "pidx is required."}, status=status.HTTP_400_BAD_REQUEST)

#     headers = {
#         "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
#         "Content-Type": "application/json"
#     }

#     payload = {"pidx": pidx}
#     response = requests.post(settings.KHALTI_VERIFY_URL, json=payload, headers=headers)

#     if response.status_code == 200:
#         data = response.json()

#         if data.get("status") == "Completed":
#             # Update the appointment as paid
#             appointment = Appointment.objects.filter(invoice_no=data["purchase_order_id"]).first()
#             if appointment:
#                 appointment.is_paid = True
#                 appointment.status = "CONFIRMED"
#                 appointment.save()
#                 return Response({"detail": "Payment verified successfully."}, status=status.HTTP_200_OK)

#         return Response({"detail": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

#     return Response({"detail": "Failed to verify payment."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def book_appointment(request):
    if request.method == 'POST':
        # Get data from request
        doctor_id = request.data.get('doctor_id')
        is_immediate = request.data.get('is_immediate', False)
        amount = request.data.get('amount')  # The amount should be provided for Khalti payment

        if not doctor_id:
            return JsonResponse({"detail": "Doctor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate if the doctor exists and has the role 'DOCTOR'
        try:
            doctor = CustomUser.objects.get(id=doctor_id, role='DOCTOR')
        except CustomUser.DoesNotExist:
            return JsonResponse({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the appointment data
        appointment_data = request.data.copy()
        appointment_data['user'] = request.user.id  
        appointment_data['doctor'] = doctor.id 

        # Set the appointment status to 'PENDING' initially
        appointment_data['status'] = 'PENDING'

        # If the appointment is immediate, remove date/time fields and mark it as confirmed
        if is_immediate:
            appointment_data.pop('appointment_date', None)
            appointment_data.pop('appointment_time', None)
            appointment_data['status'] = 'CONFIRMED'

        # Create Appointment instance and save it to get the invoice_no
        serializer = AppointmentSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save()

            # Initialize Khalti payment request
            headers = {
                "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
            }
            payment_data = {
                "amount": amount,  # The amount user is paying
                "purchase_url": settings.PURCHASE_URL,  # Your purchase URL, can be empty for now
                "return_url": settings.RETURN_URL  # URL to redirect after payment
            }

            # Send request to Khalti API for payment initiation
            response = requests.post(settings.KHALTI_INITIATE_URL, headers=headers, data=payment_data)
            if response.status_code == 200:
                response_data = response.json()
                pidx = response_data.get('pidx')  # Get the payment ID from Khalti response
                payment_url = response_data.get('payment_url')  # Get the payment URL

                # Store the pidx and payment details in the appointment
                appointment.payment_token = pidx
                appointment.payment_amount = amount
                appointment.save()

                # Prepare the response data
                response_data = {
                    "appointment_id": appointment.id,
                    "invoice_no": appointment.invoice_no,
                    "payment_url": payment_url,  # Send the payment URL to frontend
                    "pidx": pidx,  # Send pidx to frontend for later verification
                    "user_name": f"{appointment.user.first_name} {appointment.user.last_name}",
                    "doctor_name": f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}",
                    "status": appointment.status,
                    "problem_description": appointment.problem_description,
                    "created_at": appointment.created_at
                }

                # Include appointment date/time if not immediate
                if not is_immediate:
                    response_data["appointment_date"] = appointment.appointment_date
                    response_data["appointment_time"] = appointment.appointment_time

                return JsonResponse(response_data, status=status.HTTP_201_CREATED)

            else:
                return JsonResponse({"detail": "Khalti payment initiation failed."}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        appointments = Appointment.objects.filter(user=request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)



@api_view(['POST'])
def verify_payment(request):
    pidx = request.data.get('pidx')  # pidx from the frontend (should be sent after payment completion)
    amount = request.data.get('amount')  # The amount that was paid (should be sent from frontend)

    if not pidx or not amount:
        return Response({"detail": "Missing pidx or amount."}, status=status.HTTP_400_BAD_REQUEST)

    # API endpoint to verify payment with Khalti
    verify_url = "https://khalti.com/api/v2/payment/verify/"
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
    }

    data = {
        "token": pidx,  # pidx received from frontend
        "amount": amount,  # The amount paid
    }

    # Sending request to Khalti API for verification
    response = requests.post(verify_url, data=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()

        # If the payment is verified, we update the appointment status to 'CONFIRMED'
        if response_data['status'] == 'SUCCESS':
            try:
                # Find the appointment associated with the pidx (payment token)
                appointment = Appointment.objects.get(payment_token=pidx)

                # Update appointment status to 'CONFIRMED' if payment is successful
                appointment.status = 'CONFIRMED'
                appointment.save()

                # Send a response with confirmation and success message
                return Response({
                    "detail": "Payment successful and appointment confirmed.",
                    "appointment_id": appointment.id,
                    "invoice_no": appointment.invoice_no,
                    "status": appointment.status,  # "CONFIRMED"
                    "user_name": f"{appointment.user.first_name} {appointment.user.last_name}",
                    "doctor_name": f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}",
                    "appointment_date": appointment.appointment_date,
                    "appointment_time": appointment.appointment_time,
                    "problem_description": appointment.problem_description
                }, status=status.HTTP_200_OK)

            except Appointment.DoesNotExist:
                return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"detail": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({"detail": "Khalti payment verification failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#view for location
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def location_view(request):
    if request.method == 'POST':
        # Get data directly from request
        data = request.data

        # Ensure required fields exist
        required_fields = ["latitude", "longitude", "locality", "city", "state", "country"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return Response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Add authenticated user
        data["user"] = request.user.id  

        # Serialize and save the data
        serializer = LocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Location successfully saved"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Location.objects.filter(user=user_id)
        serializer = LocationSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)