from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.utils import success_response
from .models import Notification
from .serializers import NotificationSerializer, PushSubscriptionSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return success_response(data={
            'unread_count': queryset.filter(read=False).count(),
            'items': self.get_serializer(queryset, many=True).data,
        })


class NotificationMarkReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs['pk'], user=self.request.user)

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=['read'])
        return success_response(data=self.get_serializer(notification).data, message='تم تمييز الإشعار كمقروء')


class PushPublicKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        public_key = getattr(settings, 'WEB_PUSH_PUBLIC_KEY', '')
        private_key = getattr(settings, 'WEB_PUSH_PRIVATE_KEY', '')
        return success_response(data={
            'public_key': public_key,
            'enabled': bool(public_key and private_key),
        })


class PushSubscriptionView(generics.CreateAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data={}, message='تم تفعيل إشعارات الهاتف', status=status.HTTP_201_CREATED)
