from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.AssetListView.as_view(), name='asset_list'),
    path('create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('<int:pk>/', views.asset_detail_view, name='asset_detail'),
    path('<int:pk>/update/', views.AssetUpdateView.as_view(), name='asset_update'),
    path('<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
]
