from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Chat, ChatMessage, SupportConversation, SupportMessage
from .services import get_or_create_order_chat


class ReplyPreviewSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_name', 'message', 'message_type']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.username')
    reply = ReplyPreviewSerializer(source='reply_to', read_only=True)
    status = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()
    can_delete_for_everyone = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'order', 'chat', 'sender', 'sender_name', 'message',
            'message_type', 'image', 'video', 'reply_to', 'reply', 'status',
            'is_deleted', 'can_delete_for_everyone', 'delivered_at', 'read_at',
            'deleted_for_everyone_at', 'created_at',
        ]
        read_only_fields = [
            'chat', 'sender', 'sender_name', 'message_type', 'reply', 'status',
            'is_deleted', 'can_delete_for_everyone', 'delivered_at', 'read_at',
            'deleted_for_everyone_at', 'created_at',
        ]

    def validate_image(self, value):
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('ط­ط¬ظ… ط§ظ„طµظˆط±ط© ظٹط¬ط¨ ط£ظ„ط§ ظٹطھط¬ط§ظˆط² 10 ظ…ظٹط¬ط§ط¨ط§ظٹطھ')
        if value and getattr(value, 'content_type', '') not in {
            'image/jpeg', 'image/png', 'image/webp', 'image/gif',
        }:
            raise serializers.ValidationError('طµظٹط؛ط© ط§ظ„طµظˆط±ط© ط؛ظٹط± ظ…ط¯ط¹ظˆظ…ط©')
        return value

    def validate_video(self, value):
        if value and value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError('ط­ط¬ظ… ط§ظ„ظپظٹط¯ظٹظˆ ظٹط¬ط¨ ط£ظ„ط§ ظٹطھط¬ط§ظˆط² 50 ظ…ظٹط¬ط§ط¨ط§ظٹطھ')
        if value and getattr(value, 'content_type', '') not in {
            'video/mp4', 'video/webm', 'video/quicktime',
        }:
            raise serializers.ValidationError('طµظٹط؛ط© ط§ظ„ظپظٹط¯ظٹظˆ ط؛ظٹط± ظ…ط¯ط¹ظˆظ…ط©')
        return value

    def validate(self, attrs):
        text = attrs.get('message', '').strip()
        image = attrs.get('image')
        video = attrs.get('video')
        if not text and not image and not video:
            raise serializers.ValidationError('ط£ط±ط³ظ„ ظ†طµظ‹ط§ ط£ظˆ طµظˆط±ط© ط£ظˆ ظپظٹط¯ظٹظˆ')
        if image and video:
            raise serializers.ValidationError('ظٹظ…ظƒظ† ط¥ط±ط³ط§ظ„ طµظˆط±ط© ط£ظˆ ظپظٹط¯ظٹظˆ ظپظٹ ط§ظ„ط±ط³ط§ظ„ط© ط§ظ„ظˆط§ط­ط¯ط©')
        if len(text) > 2000:
            raise serializers.ValidationError({'message': 'ط§ظ„ط±ط³ط§ظ„ط© ط·ظˆظٹظ„ط© ط¬ط¯ط§ظ‹'})
        reply_to = attrs.get('reply_to')
        order = attrs.get('order')
        if reply_to and order and reply_to.order_id != order.id:
            raise serializers.ValidationError({'reply_to': 'ط§ظ„ط±ط³ط§ظ„ط© ط§ظ„ظ…ط´ط§ط± ط¥ظ„ظٹظ‡ط§ ظ„ظٹط³طھ ظپظٹ ظ‡ط°ظ‡ ط§ظ„ظ…ط­ط§ط¯ط«ط©'})
        attrs['message'] = text
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        order = validated_data['order']
        validated_data['sender'] = request.user
        validated_data['chat'] = get_or_create_order_chat(order)
        validated_data['message_type'] = (
            'image' if validated_data.get('image')
            else 'video' if validated_data.get('video')
            else 'text'
        )
        return super().create(validated_data)

    @extend_schema_field(serializers.ChoiceField(choices=['sent', 'delivered', 'seen']))
    def get_status(self, obj) -> str:
        if obj.read_at:
            return 'seen'
        if obj.delivered_at:
            return 'delivered'
        return 'sent'

    @extend_schema_field(serializers.BooleanField())
    def get_is_deleted(self, obj) -> bool:
        request = self.context.get('request')
        hidden_for_user = (
            request
            and request.user.is_authenticated
            and obj.deleted_for.filter(pk=request.user.pk).exists()
        )
        return bool(obj.deleted_for_everyone_at or hidden_for_user)

    @extend_schema_field(serializers.BooleanField())
    def get_can_delete_for_everyone(self, obj) -> bool:
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.sender_id == request.user.id
            and obj.can_delete_for_everyone()
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['is_deleted']:
            data.update({
                'message': '',
                'image': None,
                'video': None,
                'reply': None,
            })
        return data


class ConversationSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(read_only=True)
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'order_id', 'other_user', 'last_message', 'unread_count', 'updated_at']

    @extend_schema_field(serializers.DictField())
    def get_other_user(self, obj) -> dict:
        request = self.context['request']
        user = obj.chef.user if obj.customer_id == request.user.id else obj.customer
        return {
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'profile_image': user.profile_image.url if user.profile_image else None,
            'is_online': user.is_online,
            'last_seen_at': user.last_seen_at,
        }

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_last_message(self, obj) -> dict | None:
        if not getattr(obj, 'last_message_id', None):
            return None
        return {
            'id': obj.last_message_id,
            'message': obj.last_message_text,
            'message_type': obj.last_message_type,
            'created_at': obj.last_message_created_at,
        }


class ReadReceiptSerializer(serializers.Serializer):
    message_ids = serializers.ListField(child=serializers.IntegerField())
    read_at = serializers.DateTimeField()


class DeleteMessageResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    scope = serializers.ChoiceField(choices=['me', 'everyone'])


class StartChefChatResultSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    order_id = serializers.IntegerField()


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    is_support = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = [
            'id', 'sender', 'sender_name', 'is_support', 'message',
            'read_at', 'created_at',
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField())
    def get_sender_name(self, obj) -> str:
        if obj.sender.is_staff:
            return 'ط¯ط¹ظ… صنعتى'
        return obj.sender.get_full_name() or obj.sender.username

    @extend_schema_field(serializers.BooleanField())
    def get_is_support(self, obj) -> bool:
        return obj.sender.is_staff


class SupportConversationSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = SupportConversation
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_role', 'status',
            'unread_count', 'last_message', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField())
    def get_user_name(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username

    @extend_schema_field(serializers.IntegerField())
    def get_unread_count(self, obj) -> int:
        request = self.context.get('request')
        messages = obj.messages.filter(read_at__isnull=True)
        if request and request.user.is_authenticated:
            if request.user.is_staff:
                messages = messages.filter(sender__is_staff=False)
            else:
                messages = messages.filter(sender__is_staff=True)
        return messages.count()

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_last_message(self, obj) -> dict | None:
        message = obj.messages.select_related('sender').order_by('-created_at').first()
        return SupportMessageSerializer(message).data if message else None


class SupportConversationDetailSerializer(SupportConversationSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)

    class Meta(SupportConversationSerializer.Meta):
        fields = SupportConversationSerializer.Meta.fields + ['messages']


class SupportMessageCreateSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField(required=False)
    message = serializers.CharField(max_length=4000, trim_whitespace=True)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError('ط§ظƒطھط¨ ط±ط³ط§ظ„طھظƒ ط£ظˆظ„ظ‹ط§')
        return value.strip()


class SupportStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['open', 'closed'])

