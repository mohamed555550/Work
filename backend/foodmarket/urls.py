from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, Http404, JsonResponse
from django.urls import path, re_path, include
from django.views.static import serve as serve_static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import LoginView, LogoutView, ProfileView, RefreshView, RegisterView


def wants_frontend(request):
    return request.method == 'GET' and 'text/html' in request.headers.get('Accept', '')


def serve_frontend_index(_request):
    index_path = settings.FRONTEND_DIST_DIR / 'index.html'
    if not index_path.exists():
        raise Http404('Frontend build is missing. Run npm --prefix frontend run build and copy dist to backend/frontend_dist.')
    return FileResponse(index_path.open('rb'), content_type='text/html')


def serve_frontend_asset(request, path):
    return serve_static(request, path, document_root=settings.FRONTEND_DIST_DIR)


def api_or_frontend(api_view):
    view = api_view.as_view()

    def wrapped(request, *args, **kwargs):
        if wants_frontend(request):
            return serve_frontend_index(request)
        return view(request, *args, **kwargs)

    return wrapped


auth_aliases = [
    path('register', api_or_frontend(RegisterView), name='register_no_slash'),
    path('register/', api_or_frontend(RegisterView), name='register_slash'),
    path('login', api_or_frontend(LoginView), name='login_no_slash'),
    path('login/', api_or_frontend(LoginView), name='login_slash'),
    path('logout', LogoutView.as_view(), name='logout_no_slash'),
    path('logout/', LogoutView.as_view(), name='logout_slash'),
    path('refresh', RefreshView.as_view(), name='refresh_no_slash'),
    path('refresh/', RefreshView.as_view(), name='refresh_slash'),
    path('me', ProfileView.as_view(), name='me_no_slash'),
    path('me/', ProfileView.as_view(), name='me_slash'),
    path('profile', api_or_frontend(ProfileView), name='profile_no_slash'),
    path('profile/', api_or_frontend(ProfileView), name='profile_slash'),
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
    re_path(r'^(?P<path>(assets|brand|backgrounds)/.*)$', serve_frontend_asset, name='frontend_asset'),
    re_path(r'^(?P<path>(sw\.js|manifest\.webmanifest|favicon\.ico))$', serve_frontend_asset, name='frontend_file'),
    re_path(r'^(?!api/|admin/|static/|media/|healthz/).*$',
            serve_frontend_index,
            name='frontend_spa'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
