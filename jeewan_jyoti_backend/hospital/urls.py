from django.urls import path
from . import views

urlpatterns = [
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('khalti/verify/', views.verify_payment, name="verify-payment"),
    path('location/', views.location_view, name='location')
]