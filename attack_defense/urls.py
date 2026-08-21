from django.urls import path
from . import views

urlpatterns = [
    path('arena/', views.arena_pvp, name='attack_defense_arena'),
    path('admin-dashboard/', views.admin_dashboard, name='ad_admin_dashboard'),
    path('api/admin/vulnbox-status/', views.admin_vulnbox_status, name='api_vulnbox_status'),
    path('setup/', views.admin_setup, name='ad_admin_setup'),
    path('setup/sessions-table/', views.ad_sessions_table, name='ad_sessions_table'),
    path('setup/points-table/', views.ad_points_table, name='ad_points_table'),
    path('submit-flag/', views.submit_ad_flag, name='ad_submit_flag'),
    path('api/admin/uptime-chart/', views.uptime_chart_data, name='api_uptime_chart'),
]
