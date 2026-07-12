from django.urls import path
from .views import (
    EmailVerificationView,
    ChefRegisterView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RefreshView,
    RegisterView,
    SuggestionCreateView,
)
from .admin_views import AdminUserListView, AdminUserManageView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register-chef/', ChefRegisterView.as_view(), name='register_chef'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    path('forgot-password/', PasswordResetRequestView.as_view(), name='forgot_password'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='reset_password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('suggestions/', SuggestionCreateView.as_view(), name='suggestion_create'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', AdminUserManageView.as_view(), name='admin_user_manage'),
]
