from django.urls import path
from .views import (
    OpenServiceRequestListView,
    OrderCancelView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderStatusUpdateView,
    ServiceRequestChatView,
    ServiceRequestListCreateView,
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('service-requests/', ServiceRequestListCreateView.as_view(), name='service_request_list_create'),
    path('service-requests/open/', OpenServiceRequestListView.as_view(), name='service_request_open'),
    path('service-requests/<int:pk>/chat/', ServiceRequestChatView.as_view(), name='service_request_chat'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
]
