from django.urls import path
from . import views

urlpatterns = [
    path('HeartRate_Data/', views.heartrate_data_view, name='heartrate_data_view'),
    path('HRV-data/', views.HRV_data_view, name='HRV_data_view'),
    path('Spo2-data/', views.Spo2_data_view, name='Spo2_data_view'),
    path('Day_total_activity/',views.Activity_data_view, name="Activity_data_view"),
    path('Steps/', views.step_data_view, name="step_data_view"),
    path('temperature_data/', views.Temperature_data_view, name='Temperature_data_view'),
    path('sleep-data/', views.sleep_data_view, name='sleep-data'),
    path('battery-status/', views.battery_status, name='battery_status'),
    path('fetch-aggregated-data/', views.fetch_aggregated_data, name='fetch_aggregated_data'),
    path('fetch_daily_data/', views.fetch_daily_data, name='fetch_daily_data'),
    path('fetch_AI_data/', views.fetch_AI_data, name='fetch_AI_data'),
    path('dashboard/', views.fetch_latest_single_column_data, name="dashboard")
]

