from rest_framework import serializers
from .models import Review
from audit_logs.models import AuditLog
from notifications.models import Notification


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'product', 'rating', 'comment', 'user_name', 'created_at']
        read_only_fields = ['user_name', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('التقييم يجب أن يكون بين 1 و 5')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs['product']
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError('لقد قيّمت هذا المنتج من قبل')
        if not product.orderitem_set.filter(order__user=user, order__status='completed').exists():
            raise serializers.ValidationError('يجب شراء المنتج وإكمال الطلب قبل تقييمه')
        return attrs

    def create(self, validated_data):
        review = Review.objects.create(user=self.context['request'].user, **validated_data)
        product = validated_data['product']
        AuditLog.log_action(self.context['request'].user, 'review_submitted', {'product_id': product.id, 'rating': review.rating}, object_type='Review', object_id=str(review.id))
        Notification.objects.create(
            user=product.seller.user,
            title='تقييم جديد',
            content=f'تلقيت تقييماً جديداً للمنتج {product.name}',
            notification_type='message',
        )
        return review
