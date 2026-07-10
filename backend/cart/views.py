from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import CartItem
from .serializers import CartItemSerializer
from common.utils import success_response


class CartListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('product', 'product__seller')

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, message='تمت إضافة المنتج إلى السلة')


class CartItemUpdateView(generics.UpdateAPIView):
    queryset = CartItem.objects.all().select_related('product')
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs['pk'], user=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, message='تم تحديث الكمية')


class CartItemDeleteView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs['pk'], user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response(message='تم حذف المنتج من السلة')
