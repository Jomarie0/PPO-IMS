from django.urls import path
from . import views

app_name = 'cybersecurity'

urlpatterns = [
    # Blocklist Management
    path('blocklist/', views.BlocklistManagementView.as_view(), name='blocklist_management'),
    path('blocklist/add-ip/', views.AddBlockedIPView.as_view(), name='add_blocked_ip'),
    path('blocklist/add-domain/', views.AddBlockedDomainView.as_view(), name='add_blocked_domain'),
    path('blocklist/toggle/<str:model_type>/<int:pk>/', views.toggle_block_status, name='toggle_block_status'),
    
    # Whitelist Management
    path('whitelist/', views.WhitelistManagementView.as_view(), name='whitelist_management'),
    path('whitelist/add/', views.add_whitelisted_ip, name='add_whitelisted_ip'),
    path('whitelist/toggle/<int:pk>/', views.toggle_whitelist_status, name='toggle_whitelist_status'),
    
    # API Endpoints
    path('api/blocklist/', views.blocklist_api, name='blocklist_api'),
    path('agent/download/', views.agent_download, name='agent_download'),
    
    # Security Incidents
    path('incidents/', views.SecurityIncidentListView.as_view(), name='security_incidents'),
    path('incidents/create/', views.CreateSecurityIncidentView.as_view(), name='create_incident'),
    path('incidents/<int:pk>/resolve/', views.resolve_incident, name='resolve_incident'),
    
    # Analytics
    path('analytics/', views.login_analytics, name='login_analytics'),
]
