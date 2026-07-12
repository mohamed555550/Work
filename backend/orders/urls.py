from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView, OrderStatusUpdateView, OrderCancelView

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
]
