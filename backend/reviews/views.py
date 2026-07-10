from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from common.throttles import ReviewCreationThrottle
from common.utils import success_response


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ReviewCreationThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(data=response.data, message='تم إضافة التقييم بنجاح')


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_id']).select_related('user')

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)
