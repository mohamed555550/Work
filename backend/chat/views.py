from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.utils import error_response, success_response
from notifications.models import Notification
from orders.models import Order
from .models import Chat, ChatMessage, SupportConversation, SupportMessage
from .serializers import (
    ChatMessageSerializer,
    ConversationSerializer,
    DeleteMessageResultSerializer,
    ReadReceiptSerializer,
    StartChefChatResultSerializer,
    SupportConversationDetailSerializer,
    SupportConversationSerializer,
    SupportMessageCreateSerializer,
    SupportMessageSerializer,
    SupportStatusSerializer,
)
from .services import get_or_create_order_chat, mark_messages_read
from sellers.models import SellerProfile


def can_access_order_chat(user, order):
    return user.is_staff or order.user_id == user.id or order.seller.user_id == user.id


def broadcast_status(order_id, message_ids, status_name, timestamp):
    async_to_sync(get_channel_layer().group_send)(
        f'order_chat_{order_id}',
        {
            'type': 'chat.status',
            'message_ids': message_ids,
            'status': status_name,
            'timestamp': timestamp.isoformat(),
        },
    )


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        last_message = ChatMessage.objects.filter(
            chat=OuterRef('pk'),
            deleted_for_everyone_at__isnull=True,
        ).order_by('-created_at')
        queryset = Chat.objects.filter(
            Q(customer=user) | Q(chef__user=user)
        ).select_related('customer', 'chef__user', 'order').annotate(
            last_message_id=Subquery(last_message.values('id')[:1]),
            last_message_text=Subquery(last_message.values('message')[:1]),
            last_message_type=Subquery(last_message.values('message_type')[:1]),
            last_message_created_at=Subquery(last_message.values('created_at')[:1]),
            unread_count=Count(
                'messages',
                filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=user),
                distinct=True,
            ),
        )
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(customer__username__icontains=search)
                | Q(customer__first_name__icontains=search)
                | Q(customer__last_name__icontains=search)
                | Q(chef__name__icontains=search)
                | Q(messages__message__icontains=search)
            ).distinct()
        return queryset.order_by('-updated_at')


class ChatListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_order(self):
        order = get_object_or_404(
            Order.objects.select_related('seller__user', 'user'),
            pk=self.kwargs['order_id'],
        )
        if not can_access_order_chat(self.request.user, order):
            return None
        return order

    def get_queryset(self):
        order = self.get_order()
        if not order:
            return ChatMessage.objects.none()
        return ChatMessage.objects.filter(order=order).exclude(
            deleted_for=self.request.user
        ).select_related('sender', 'reply_to__sender').prefetch_related('deleted_for')

    def list(self, request, *args, **kwargs):
        if not self.get_order():
            return error_response('ط؛ظٹط± ظ…طµط±ط­', status=403)
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class ChatCreateView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        order = get_object_or_404(
            Order.objects.select_related('seller__user', 'user'),
            pk=request.data.get('order'),
        )
        if not can_access_order_chat(request.user, order):
            return error_response('ط؛ظٹط± ظ…طµط±ط­', status=403)
        response = super().create(request, *args, **kwargs)
        recipient = order.seller.user if request.user == order.user else order.user
        Notification.objects.create(
            user=recipient,
            title='ط±ط³ط§ظ„ط© ط¬ط¯ظٹط¯ط©',
            content=f'ظ„ط¯ظٹظƒ ط±ط³ط§ظ„ط© ط¬ط¯ظٹط¯ط© ط¨ط®طµظˆطµ ط§ظ„ط·ظ„ط¨ ط±ظ‚ظ… {order.id}',
            notification_type='message',
            order=order,
        )
        return success_response(data=response.data, message='طھظ… ط¥ط±ط³ط§ظ„ ط§ظ„ط±ط³ط§ظ„ط©', status=201)


class MarkChatReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=ReadReceiptSerializer)
    def post(self, request, order_id):
        order = get_object_or_404(
            Order.objects.select_related('seller__user', 'user'),
            pk=order_id,
        )
        if not can_access_order_chat(request.user, order):
            return error_response('ط؛ظٹط± ظ…طµط±ط­', status=403)
        chat = get_or_create_order_chat(order)
        message_ids, read_at = mark_messages_read(chat, request.user)
        if message_ids:
            broadcast_status(order.id, message_ids, 'seen', read_at)
        return success_response(data={'message_ids': message_ids, 'read_at': read_at})


class DeleteMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=DeleteMessageResultSerializer)
    def delete(self, request, pk):
        message = get_object_or_404(
            ChatMessage.objects.select_related('order__seller__user', 'order__user'),
            pk=pk,
        )
        if not can_access_order_chat(request.user, message.order):
            return error_response('ط؛ظٹط± ظ…طµط±ط­', status=403)
        scope = request.query_params.get('scope', 'me')
        if scope == 'everyone':
            if message.sender_id != request.user.id:
                return error_response('ظٹظ…ظƒظ† ظ„ظ„ظ…ط±ط³ظ„ ظپظ‚ط· ط­ط°ظپ ط§ظ„ط±ط³ط§ظ„ط© ظ„ظ„ط¬ظ…ظٹط¹', status=403)
            if not message.can_delete_for_everyone():
                return error_response('ط§ظ†طھظ‡طھ ظ…ظ‡ظ„ط© ط­ط°ظپ ط§ظ„ط±ط³ط§ظ„ط© ظ„ظ„ط¬ظ…ظٹط¹', status=400)
            if message.image:
                message.image.delete(save=False)
            if message.video:
                message.video.delete(save=False)
            message.message = ''
            message.image = None
            message.video = None
            message.deleted_for_everyone_at = timezone.now()
            message.save(update_fields=[
                'message', 'image', 'video', 'deleted_for_everyone_at',
            ])
            async_to_sync(get_channel_layer().group_send)(
                f'order_chat_{message.order_id}',
                {'type': 'chat.deleted', 'message_id': message.id, 'scope': 'everyone'},
            )
        elif scope == 'me':
            message.deleted_for.add(request.user)
        else:
            return error_response('ظ†ط·ط§ظ‚ ط§ظ„ط­ط°ظپ ط؛ظٹط± طµط§ظ„ط­', status=400)
        return success_response(data={'id': message.id, 'scope': scope})


class StartChefChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=StartChefChatResultSerializer)
    def post(self, request, chef_id):
        chef = get_object_or_404(SellerProfile, pk=chef_id, approved='approved')
        if chef.user_id == request.user.id:
            return error_response('ظ„ط§ ظٹظ…ظƒظ†ظƒ ط¨ط¯ط، ظ…ط­ط§ط¯ط«ط© ظ…ط¹ ط­ط³ط§ط¨ظƒ', status=400)
        order = Order.objects.filter(
            user=request.user,
            seller=chef,
        ).order_by('-created_at').first()
        if not order:
            order = Order.objects.create(
                user=request.user,
                seller=chef,
                total_price=0,
                pickup_address=chef.pickup_address or '',
            )
        chat = get_or_create_order_chat(order)
        return success_response(data={'chat_id': chat.id, 'order_id': order.id})


def support_conversation_queryset():
    return SupportConversation.objects.select_related('user').prefetch_related('messages__sender')


def mark_support_messages_read(conversation, user):
    return conversation.messages.filter(
        read_at__isnull=True,
    ).exclude(sender=user).update(read_at=timezone.now())


class OwnSupportConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=SupportConversationDetailSerializer)
    def get(self, request):
        conversation, _ = SupportConversation.objects.get_or_create(user=request.user)
        mark_support_messages_read(conversation, request.user)
        conversation = get_object_or_404(support_conversation_queryset(), pk=conversation.pk)
        return success_response(
            data=SupportConversationDetailSerializer(
                conversation,
                context={'request': request},
            ).data,
        )


class AdminSupportConversationListView(generics.ListAPIView):
    serializer_class = SupportConversationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = support_conversation_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(messages__message__icontains=search)
            ).distinct()
        status_name = self.request.query_params.get('status', '').strip()
        if status_name in {'open', 'closed'}:
            queryset = queryset.filter(status=status_name)
        return queryset.order_by('-updated_at')


class AdminSupportConversationDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_conversation(self, pk):
        return get_object_or_404(support_conversation_queryset(), pk=pk)

    @extend_schema(responses=SupportConversationDetailSerializer)
    def get(self, request, pk):
        conversation = self.get_conversation(pk)
        mark_support_messages_read(conversation, request.user)
        return success_response(
            data=SupportConversationDetailSerializer(
                conversation,
                context={'request': request},
            ).data,
        )

    @extend_schema(request=SupportStatusSerializer, responses=SupportConversationDetailSerializer)
    def patch(self, request, pk):
        serializer = SupportStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = self.get_conversation(pk)
        conversation.status = serializer.validated_data['status']
        conversation.save(update_fields=['status', 'updated_at'])
        return success_response(
            data=SupportConversationDetailSerializer(
                conversation,
                context={'request': request},
            ).data,
            message='طھظ… طھط­ط¯ظٹط« ط­ط§ظ„ط© ظ…ط­ط§ط¯ط«ط© ط§ظ„ط¯ط¹ظ…',
        )


class SupportMessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=SupportMessageCreateSerializer, responses=SupportMessageSerializer)
    def post(self, request):
        serializer = SupportMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation_id = serializer.validated_data.get('conversation_id')

        if request.user.is_staff:
            if not conversation_id:
                return error_response('ط§ط®طھط± ظ…ط­ط§ط¯ط«ط© ط§ظ„ط¹ظ…ظٹظ„ ط£ظˆظ„ظ‹ط§', status=400)
            conversation = get_object_or_404(
                SupportConversation.objects.select_related('user'),
                pk=conversation_id,
            )
        else:
            conversation, _ = SupportConversation.objects.get_or_create(user=request.user)

        if conversation.status == 'closed' and not request.user.is_staff:
            conversation.status = 'open'

        message = SupportMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            message=serializer.validated_data['message'],
        )
        conversation.save(update_fields=['status', 'updated_at'])

        if request.user.is_staff:
            if conversation.user_id != request.user.id:
                Notification.objects.create(
                    user=conversation.user,
                    title='ط±ط¯ ط¬ط¯ظٹط¯ ظ…ظ† ط¯ط¹ظ… صنعتى',
                    content='ظپط±ظٹظ‚ ط§ظ„ط¯ط¹ظ… ط±ط¯ ط¹ظ„ظ‰ ط±ط³ط§ظ„طھظƒ. ط§ظپطھط­ ظ…ط­ط§ط¯ط«ط© ط§ظ„ط¯ط¹ظ… ظ„ظ…ط´ط§ظ‡ط¯ط© ط§ظ„ط±ط¯.',
                    notification_type='message',
                )
        else:
            admins = get_user_model().objects.filter(
                is_staff=True,
                is_active=True,
            ).exclude(pk=request.user.pk)
            Notification.objects.bulk_create([
                Notification(
                    user=admin,
                    title='ط±ط³ط§ظ„ط© ط¯ط¹ظ… ط¬ط¯ظٹط¯ط©',
                    content=f'ط±ط³ط§ظ„ط© ط¬ط¯ظٹط¯ط© ظ…ظ† {request.user.get_full_name() or request.user.username}',
                    notification_type='message',
                )
                for admin in admins
            ])

        return success_response(
            data=SupportMessageSerializer(message).data,
            message='طھظ… ط¥ط±ط³ط§ظ„ ط±ط³ط§ظ„طھظƒ ط¥ظ„ظ‰ ط¯ط¹ظ… صنعتى',
            status=201,
        )

