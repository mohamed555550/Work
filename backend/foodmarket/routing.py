from django.urls import path
from chat.consumers import OrderChatConsumer
from notifications.consumers import NotificationConsumer


websocket_urlpatterns = [
    path('ws/orders/<int:order_id>/chat/', OrderChatConsumer.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]
