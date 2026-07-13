import os
from decimal import Decimal
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'unsafe-secret-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'DJANGO_ALLOWED_HOSTS',
        'localhost,127.0.0.1,testserver,mohamed555550.github.io,raw.githack.com',
    ).split(',')
    if host.strip()
]
for render_host in (
    os.getenv('RENDER_EXTERNAL_HOSTNAME'),
    os.getenv('BACKEND_EXTERNAL_HOSTNAME'),
):
    if render_host and render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(render_host)

if not DEBUG and SECRET_KEY == 'unsafe-secret-change-me':
    raise RuntimeError('DJANGO_SECRET_KEY must be configured when DEBUG is disabled')

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt.token_blacklist',
    'channels',
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'users',
    'sellers',
    'products',
    'orders',
    'reviews',
    'cart',
    'favorites',
    'notifications.apps.NotificationsConfig',
    'chat.apps.ChatConfig',
    'audit_logs',
    'common.apps.CommonConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.remove('whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'foodmarket.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodmarket.wsgi.application'
ASGI_APPLICATION = 'foodmarket.asgi.application'

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    parsed_database = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed_database.path.lstrip('/'),
            'USER': parsed_database.username or '',
            'PASSWORD': parsed_database.password or '',
            'HOST': parsed_database.hostname or '',
            'PORT': parsed_database.port or 5432,
            'CONN_MAX_AGE': 60,
            'OPTIONS': {'sslmode': os.getenv('POSTGRES_SSLMODE', 'require')},
        }
    }
elif os.getenv('USE_SQLITE', 'False').lower() in ('1', 'true', 'yes'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'foodmarket'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
FRONTEND_DIST_DIR = BASE_DIR / 'frontend_dist'

STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if os.getenv('CLOUDINARY_URL')
            else 'django.core.files.storage.FileSystemStorage'
        )
    },
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173,https://mohamed555550.github.io,https://raw.githack.com',
    ).split(',')
    if origin.strip()
]
for frontend_origin in (
    os.getenv('FRONTEND_URL'),
    f"https://{os.getenv('FRONTEND_EXTERNAL_HOSTNAME')}" if os.getenv('FRONTEND_EXTERNAL_HOSTNAME') else '',
):
    if frontend_origin and frontend_origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(frontend_origin)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173,https://mohamed555550.github.io,https://raw.githack.com',
    ).split(',')
    if origin.strip()
]
for frontend_origin in (
    os.getenv('FRONTEND_URL'),
    f"https://{os.getenv('FRONTEND_EXTERNAL_HOSTNAME')}" if os.getenv('FRONTEND_EXTERNAL_HOSTNAME') else '',
):
    if frontend_origin and frontend_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(frontend_origin)

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
USE_REDIS = os.getenv('USE_REDIS', 'False').lower() in ('1', 'true', 'yes')
if USE_REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'TIMEOUT': 300,
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [REDIS_URL]},
        }
    }
else:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}

FRONTEND_URL = (
    os.getenv('FRONTEND_URL')
    or (f"https://{os.getenv('FRONTEND_EXTERNAL_HOSTNAME')}" if os.getenv('FRONTEND_EXTERNAL_HOSTNAME') else None)
    or 'http://localhost:5173'
)
EMAIL_VERIFICATION_REQUIRED = os.getenv(
    'EMAIL_VERIFICATION_REQUIRED',
    'False' if DEBUG else 'True',
).lower() in ('1', 'true', 'yes')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@sanati.local')
SUGGESTIONS_EMAIL = os.getenv('SUGGESTIONS_EMAIL', 'elnono55555@gmail.com')
WEB_PUSH_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
WEB_PUSH_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '').replace('\\n', '\n')
WEB_PUSH_SUBJECT = os.getenv('VAPID_SUBJECT', f'mailto:{SUGGESTIONS_EMAIL}')
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_TIMEOUT = 10

PLATFORM_COMMISSION_RATE = Decimal(os.getenv('PLATFORM_COMMISSION_RATE', '10.00'))
if not 0 <= PLATFORM_COMMISSION_RATE <= 100:
    raise RuntimeError('PLATFORM_COMMISSION_RATE must be between 0 and 100')

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() in ('1', 'true', 'yes')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    if os.getenv('DJANGO_BEHIND_PROXY', 'False').lower() in ('1', 'true', 'yes'):
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 24,
    'EXCEPTION_HANDLER': 'common.utils.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'auth': '5/min',
        'order_create': '10/hour',
        'review_create': '10/hour',
        'anon': '60/min',
        'user': '300/min',
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'صنعتى Marketplace API',
    'DESCRIPTION': 'Secure API for customers, workers, and administrators.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'ENUM_NAME_OVERRIDES': {
        'OrderStateEnum': 'orders.models.Order.STATUS_CHOICES',
        'MessageDeliveryStateEnum': ['sent', 'delivered', 'seen'],
        'SupportConversationStatusEnum': 'chat.models.SupportConversation.STATUS_CHOICES',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=45),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
