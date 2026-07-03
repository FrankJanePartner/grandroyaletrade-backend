import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_config(name, default=None, cast=None):
    value = os.environ.get(name, default)
    if value is None:
        return None
    if cast is bool:
        return str(value).lower() in {"1", "true", "yes", "on"}
    if callable(cast):
        return cast(value)
    return value


SECRET_KEY = get_config('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = get_config('DEBUG', True, bool)

ALLOWED_HOSTS = ['grandroyaletrade-backend-ashy.vercel.app']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'corsheaders',
    
    'apps.users',
    'apps.finance',
    'apps.kyc',
    'apps.admin_panel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.users.auth.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# CORS
CORS_ALLOWED_ORIGINS = get_config(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000',
    lambda v: [s.strip() for s in v.split(',')]
)

# JWT
JWT_SECRET = get_config('JWT_SECRET', 'jwt-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID = get_config('GOOGLE_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_CLIENT_SECRET = get_config('GOOGLE_OAUTH_CLIENT_SECRET', '')

# Email (optional - for password reset)
EMAIL_BACKEND = get_config('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = get_config('EMAIL_HOST', '')
EMAIL_PORT = get_config('EMAIL_PORT', 587, int)
EMAIL_USE_TLS = get_config('EMAIL_USE_TLS', True, bool)
EMAIL_HOST_USER = get_config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_config('EMAIL_HOST_PASSWORD', '')
