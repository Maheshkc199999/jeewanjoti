from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.permissions import IsAdminUser
from .utils import generate_otp, store_otp, validate_otp
from .serializers import RegisterSerializer, LoginSerializer,ProfileImageSerializer,ProfileUpdateSerializer



User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]  
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        # Validate user data
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            role = serializer.validated_data['role']

            if User.objects.filter(email=email).exists():
                return Response({"detail": "Email already in use."}, status=status.HTTP_400_BAD_REQUEST)

            email_otp = generate_otp()
            cache.set(f"otp:{email}", {"otp": email_otp, "user_data": serializer.validated_data}, timeout=300)

            send_mail(
                'Email Verification OTP',
                f'Your OTP for email verification is: {email_otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response(
                {
                    "message": "OTP sent to your email. Please verify to complete registration.",
                    "email": email,
                    "role": role  # Include role in response
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        email = request.data.get('email')
        email_otp = request.data.get('email_otp')

        if not email or not email_otp:
            return Response(
                {"detail": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cached_data = cache.get(f"otp:{email}")
        if not cached_data:
            return Response(
                {"detail": "OTP expired or not requested."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cached_data["otp"] != email_otp:
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_data = cached_data["user_data"]
        user_data.pop('confirm_password', None) 

        try:
            user = User.objects.create_user(**user_data)
            user.is_email_verified = True
            user.save()

            cache.delete(f"otp:{email}")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            role = user.role  # Get user role

            response_data = {
                "message": "Email verified successfully and user registered.",
                "user": {
                    "email": user.email,
                    "role": role,
                    "birthdate": user.birthdate,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "gender": user.gender,
                },
                "access": access_token,
                "refresh": refresh_token,
            }

            if role == "USER":
                response_data["user"].update({
                    "height": user.height,
                    "weight": user.weight,
                    "blood_group": user.blood_group
                })
            elif role == "DOCTOR":
                response_data["user"].update({
                    "specialization": user.specialization,
                    "license_number": user.license_number,
                    "hospital_name": user.hospital_name,
                    "experience": user.experience,
                    "education": user.education,
                    "description": user.description,
                    "phone_number":user.phone_number
                })
            elif role == "NURSE":
                response_data["user"].update({
                    "license_number": user.license_number,
                    "hospital_name": user.hospital_name,
                    "experience": user.experience,
                    "education": user.education,
                    "description": user.description,
                    "phone_number":user.phone_number
                })
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"An error occurred during user registration: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "User logged in successfully",
                    "user": {
                        "email": user.email,
                        "birthdate":user.birthdate,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "gender": user.gender,
                        "height": user.height,
                        "weight": user.weight,
                        "blood_group": user.blood_group,
                        "is_superuser": user.is_superuser,
                        
                    },
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResendOtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(email=email).exists():
            return Response({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        new_otp = generate_otp()
        store_otp(email, new_otp)

        send_mail(
            'Resend OTP - Email Verification',
            f'Your new OTP is: {new_otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({"message": "New OTP sent to your email."}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(email=email).exists():
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

      
        reset_otp = generate_otp()
        store_otp(email, reset_otp)

       
        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is: {reset_otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset OTP sent."}, status=status.HTTP_200_OK)
    
class VerifyResetOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        email_otp = request.data.get('email_otp') 

        if not all([email, email_otp]):  
            return Response({"detail": "Email and email_otp are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        is_valid, message = validate_otp(email, email_otp) 
        if not is_valid:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        cache.set(f"verified_reset:{email}", True, timeout=300)  

        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)



class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password') 

        if not all([email, new_password, confirm_password]):
            return Response(
                {"detail": "Email, new password, and confirm password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if not cache.get(f"verified_reset:{email}"):
            return Response(
                {"detail": "OTP verification required before resetting password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

    
            cache.delete(f"verified_reset:{email}")

            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only superusers
    authentication_classes = [JWTAuthentication]

    def delete(self, request):
        user_id = request.data.get('id')
        
        # If the user is not a superuser, they can only delete their own account
        if not request.user.is_superuser and not user_id:
            user_id = request.user.id
        
        if request.user.is_superuser and not user_id:
            return Response({"detail": "User ID is required for superuser."}, status=status.HTTP_400_BAD_REQUEST)

        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Prevent superuser from deleting themselves
            if user == request.user:
                return Response({"detail": "You cannot delete your own account"}, status=status.HTTP_403_FORBIDDEN)

            try:
                user.delete()
                return Response({"message": "User account deleted successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"detail": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Authenticated users only
    authentication_classes = [JWTAuthentication]

    def patch(self, request):
        user_id = request.data.get('id')

        # Normal users can only update their own profile
        if not request.user.is_superuser:
            user = request.user  
        else:
            # Superuser/Admin can update their own profile or another user's profile
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                user = request.user  # If no ID provided, update their own profile

        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ProfileImageUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    def patch(self, request):
        user = request.user
        serializer = ProfileImageSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Delete the old profile image if it exists
            if user.profile_image:
                user.profile_image.delete()

            # Save the new profile image
            serializer.save()
            return Response(
                {"message": "Profile image updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#user list view for dashboard
class UserListView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        if not request.user.is_superuser:  # Ensure only admins can access
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all()
        serializer = RegisterSerializer(users, many=True)  # Serialize multiple users
        return Response(serializer.data, status=status.HTTP_200_OK)



#fetch doctor to all authencated user
class DoctorListView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Ensure only authenticated users can access this view
        if not request.user.is_authenticated:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Fetch only users with the role 'DOCTOR'
        users = User.objects.filter(role='DOCTOR')  # Adjust the filter based on your actual role field
        serializer = RegisterSerializer(users, many=True)  # Serialize multiple users
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    
#user email and profile photo for the dashboard

class UserEmailProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users
    authentication_classes = [JWTAuthentication]  # JWT authentication

    def get(self, request):
        # Get user_id from query parameters
        user_id = request.query_params.get('user_id')

        if request.user.is_superuser:
            # If the user is a superuser, they must provide a user_id
            if not user_id:
                return Response(
                    {"error": "Superuser must provide 'user_id' as a query parameter."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = get_object_or_404(User, id=user_id)

        else:
            # Regular authenticated users can only access their own profile
            if user_id and int(user_id) != request.user.id:
                return Response(
                    {"error": "You do not have permission to access this resource."},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = request.user  # Fetch own profile

        # Construct the response data
        response_data = {
            "email": user.email,
            "profile_image": request.build_absolute_uri(user.profile_image.url)
            if getattr(user, "profile_image", None) else None
        }

        return Response(response_data, status=status.HTTP_200_OK)