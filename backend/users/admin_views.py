from rest_framework import generics, permissions

from common.utils import error_response, success_response
from .models import User
from .serializers import UserSerializer


class AdminUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return User.objects.order_by('-date_joined')

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class AdminUserManageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        role = request.data.get('role')
        is_active = request.data.get('is_active')
        update_fields = []
        if role in {'user', 'seller', 'admin'}:
            user.role = role
            user.is_staff = role == 'admin'
            update_fields.extend(['role', 'is_staff'])
        if is_active is not None:
            user.is_active = bool(is_active)
            update_fields.append('is_active')
        if update_fields:
            user.save(update_fields=list(set(update_fields)))
        return success_response(data=self.get_serializer(user).data, message='تم تحديث المستخدم')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return error_response('لا يمكن حذف حسابك الحالي', status=400)
        user.delete()
        return success_response(message='تم حذف المستخدم')
