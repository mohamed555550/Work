from rest_framework import serializers
from .models import Notification, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'content', 'notification_type', 'read', 'order', 'created_at']


class PushSubscriptionSerializer(serializers.ModelSerializer):
    keys = serializers.DictField(write_only=True)

    class Meta:
        model = PushSubscription
        fields = ['endpoint', 'keys']

    def validate_keys(self, value):
        if not value.get('p256dh') or not value.get('auth'):
            raise serializers.ValidationError('بيانات اشتراك الإشعارات غير كاملة')
        return value

    def create(self, validated_data):
        keys = validated_data.pop('keys')
        subscription, _ = PushSubscription.objects.update_or_create(
            endpoint=validated_data['endpoint'],
            defaults={
                'user': self.context['request'].user,
                'p256dh': keys['p256dh'],
                'auth': keys['auth'],
                'user_agent': self.context['request'].META.get('HTTP_USER_AGENT', '')[:1000],
            },
        )
        return subscription
