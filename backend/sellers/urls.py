from django.urls import path
from .views import (
    SellerAdminListView,
    SellerApplicationView,
    SellerApproveView,
    SellerProfileView,
    SellerPublicDetailView,
    SellerPublicListView,
    SellerFavoriteView,
    SellerFollowView,
    GovernorateListView,
    SellerWorkGalleryDeleteView,
    SellerWorkGalleryView,
)

urlpatterns = [
    path('locations/', GovernorateListView.as_view(), name='governorate_list'),
    path('apply/', SellerApplicationView.as_view(), name='seller_apply'),
    path('', SellerPublicListView.as_view(), name='seller_public_list'),
    path('<int:pk>/', SellerPublicDetailView.as_view(), name='seller_public_detail'),
    path('profile/', SellerProfileView.as_view(), name='seller_profile'),
    path('profile/gallery/', SellerWorkGalleryView.as_view(), name='seller_work_gallery'),
    path('profile/gallery/<int:pk>/', SellerWorkGalleryDeleteView.as_view(), name='seller_work_gallery_delete'),
    path('admin/pending/', SellerAdminListView.as_view(), name='seller_pending_list'),
    path('<int:pk>/approve/', SellerApproveView.as_view(), name='seller_approve'),
    path('<int:pk>/follow/', SellerFollowView.as_view(), name='seller_follow'),
    path('<int:pk>/favorite/', SellerFavoriteView.as_view(), name='seller_favorite'),
]
