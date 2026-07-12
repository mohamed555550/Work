from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'action', 'object_type', 'object_id', 'metadata', 'created_at']
