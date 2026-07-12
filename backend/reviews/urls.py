from django.urls import path
from .views import ReviewCreateView, ProductReviewListView

urlpatterns = [
    path('create/', ReviewCreateView.as_view(), name='review_create'),
    path('product/<int:product_id>/', ProductReviewListView.as_view(), name='product_reviews'),
]
