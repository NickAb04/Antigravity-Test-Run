from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('submit/', views.submit_flag, name='submit_flag'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/leaderboard/', views.leaderboard_data, name='leaderboard_data'),
]
