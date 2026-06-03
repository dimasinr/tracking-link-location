from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from dashboard.views import dashboard_home
from tracking.views import (
    link_list, link_create, link_toggle, link_delete,
    result_list, result_detail, consent_view,
    export_hits_csv, export_hits_excel
)
from api.views import track_location, dashboard_stats_api
from accounts.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('dashboard'), name='root_redirect'),
    path('dashboard/', dashboard_home, name='dashboard'),
    
    path('tracking-links/', link_list, name='link_list'),
    path('tracking-links/create', link_create, name='link_create'),
    path('tracking-links/<int:pk>/toggle/', link_toggle, name='link_toggle'),
    path('tracking-links/<int:pk>/delete/', link_delete, name='link_delete'),
    
    path('tracking-results/', result_list, name='result_list'),
    path('tracking-results/<int:pk>/', result_detail, name='result_detail'),
    path('tracking-results/export/csv/', export_hits_csv, name='export_hits_csv'),
    path('tracking-results/export/excel/', export_hits_excel, name='export_hits_excel'),
    
    path('t/<code>', consent_view, name='consent_view'),
    
    path('api/track/', track_location, name='track_location'),
    path('api/dashboard/stats/', dashboard_stats_api, name='dashboard_stats_api'),
    
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
]
