from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import LoginView, LogoutView, ProfileView, RefreshView, RegisterView

auth_aliases = [
    path('register', RegisterView.as_view(), name='register_no_slash'),
    path('register/', RegisterView.as_view(), name='register_slash'),
    path('login', LoginView.as_view(), name='login_no_slash'),
    path('login/', LoginView.as_view(), name='login_slash'),
    path('logout', LogoutView.as_view(), name='logout_no_slash'),
    path('logout/', LogoutView.as_view(), name='logout_slash'),
    path('refresh', RefreshView.as_view(), name='refresh_no_slash'),
    path('refresh/', RefreshView.as_view(), name='refresh_slash'),
    path('me', ProfileView.as_view(), name='me_no_slash'),
    path('me/', ProfileView.as_view(), name='me_slash'),
    path('profile', ProfileView.as_view(), name='profile_no_slash'),
    path('profile/', ProfileView.as_view(), name='profile_slash'),
]

urlpatterns = [
    path('healthz/', lambda request: JsonResponse({'ok': True}), name='healthz'),
    path('admin/', admin.site.urls),
    *auth_aliases,
    path('api/v1/', include((auth_aliases, 'auth_aliases'))),
    path('api/users/', include('users.urls')),
    path('api/sellers/', include('sellers.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/favorites/', include('favorites.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/audit/', include('audit_logs.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/sellers/', include('sellers.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
    path('api/v1/cart/', include('cart.urls')),
    path('api/v1/favorites/', include('favorites.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/chat/', include('chat.urls')),
    path('api/v1/audit/', include('audit_logs.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
