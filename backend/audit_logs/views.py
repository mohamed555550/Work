from rest_framework import generics, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer
from common.utils import success_response


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)
