from django.urls import path
from .views import (
    AISearchView,
    AIRecommendationView,
    ProductListView,
    ProductCreateView,
    ProductDetailView,
    AdminProductListView,
    ProductManageView,
    SellerProductListView,
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('ai-search/', AISearchView.as_view(), name='ai_search'),
    path('recommendations/', AIRecommendationView.as_view(), name='ai_recommendations'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('seller/', SellerProductListView.as_view(), name='seller_product_list'),
    path('admin/all/', AdminProductListView.as_view(), name='admin_product_list'),
    path('<int:pk>/manage/', ProductManageView.as_view(), name='product_manage'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
