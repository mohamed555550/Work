from django.urls import path
from .views import NotificationListView, NotificationMarkReadView, PushPublicKeyView, PushSubscriptionView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('push/public-key/', PushPublicKeyView.as_view(), name='push_public_key'),
    path('push/subscribe/', PushSubscriptionView.as_view(), name='push_subscribe'),
]
