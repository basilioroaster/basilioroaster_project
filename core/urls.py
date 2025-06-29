from django.urls import path
from . import views
from .views import ( # Import the new Class-Based Views
    MqttDeviceListView, 
    MqttDeviceCreateView, 
    MqttDeviceUpdateView, 
    MqttDeviceDeleteView
    )

# This file defines the specific URL endpoints for the 'core' app.

urlpatterns = [
    # [RECOMMENDATION] Add this new path for your navigation dashboard.
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # This path calls the 'create_purchase_order' view function.
    path('purchase-orders/create/', views.create_purchase_order, name='create_purchase_order'),
    
    # This path calls the 'create_gcb_purchase_order' view function.
    path('gcb-purchase-orders/create/', views.create_gcb_purchase_order, name='create_gcb_purchase_order'),
    # URL for the device list page (e.g., /app/devices/)
    path('devices/', MqttDeviceListView.as_view(), name='device_list'),

    # URL for the "add device" page
    path('devices/add/', MqttDeviceCreateView.as_view(), name='device_add'),

    # URL for the "edit device" page. <pk> is the primary key of the device.
    path('devices/<str:pk>/edit/', MqttDeviceUpdateView.as_view(), name='device_edit'),

    # URL for the "delete device" page
    path('devices/<str:pk>/delete/', MqttDeviceDeleteView.as_view(), name='device_delete'),

     # --- [NEW] URL for the "Live Label" HMI page ---
    path('hmi/live-label/', views.live_label_view, name='live_label'),
    
    # --- [NEW] URL for the API endpoint ---
    path('api/latest-lot/', views.get_latest_lot_api, name='api_latest_lot'),
    path('lots/<str:lot_identifier>/', views.lot_detail_view, name='lot_detail'),

]