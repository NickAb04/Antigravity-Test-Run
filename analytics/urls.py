from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.ai_dashboard, name='ai_dashboard'),
    path('export-csv/', views.export_submissions_csv, name='export_submissions_csv'),
]
