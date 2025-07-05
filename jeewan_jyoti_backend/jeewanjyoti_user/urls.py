from django.urls import path
from .views import RegisterView,VerifyOtpView,LoginView, ResendOtpView, ForgotPasswordView, VerifyResetOtpView,ResetPasswordView,DeleteAccountView,ProfileImageUpdateView,ProfileUpdateView, UserListView,DoctorListView,UserEmailProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otpVerification/', VerifyOtpView.as_view(), name='otpVerification'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('resend-otp/', ResendOtpView.as_view(), name='resend-otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('resetotpVerification/', VerifyResetOtpView.as_view(), name='resetotpVerification'),
    path('delete-account/', DeleteAccountView.as_view(), name='DeleteAccount'),
    path('profile-update/', ProfileUpdateView.as_view(), name='profileupdate'),
    path('profile-image/', ProfileImageUpdateView.as_view(), name='imageupdate'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'), 
    path('useremailprofile/', UserEmailProfileView.as_view(), name='get-email-profile'),
    path('doctorlist/', DoctorListView.as_view(), name='doctor_list')
]
