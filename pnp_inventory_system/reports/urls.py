from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='home'),
    path('monthly/', views.monthly_report, name='monthly'),
    path('quarterly/', views.quarterly_report, name='quarterly'),
    path('custom/', views.custom_report, name='custom'),
    path('history/', views.report_history, name='history'),
]
