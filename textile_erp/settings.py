# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'django-insecure-qe*1+!(k$m&2qnuk&wy47k@&)xr*442=mhvhu+&9dn_p_r^2o4'
DEBUG = True

ALLOWED_HOSTS = ['*']

# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ERP apps
    'django.contrib.humanize',
    'core',
    'orders',
    'customers',
    'products',
    'warehouse',
    'production',
    'users',
    # 'inventory',  # اگر اپ inventory داری این را فعال کن
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'users.middleware.UserPermissionMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://*.googleusercontent.com',
    'https://*.aistudio.google',
    'https://*.studio',
]

ROOT_URLCONF = 'textile_erp.urls'

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # اگر قالب‌های سراسری در <project_root>/templates قرار دارند این مسیر را اضافه کن
        'DIRS': [ BASE_DIR / "templates", ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'textile_erp.wsgi.application'

# DATABASE
# Fallback to SQLite in development/sandboxed environments where PostgreSQL server is not available
USE_POSTGRES = os.environ.get('DB_ENGINE') == 'postgresql'

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'textile_db'),
            'USER': os.environ.get('DB_USER', 'textile_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', '1234'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES (مهم برای رفع 404)
STATIC_URL = '/static/'

# مسیری که در توسعه فایل‌های استاتیک را از آن می‌خوانیم
STATICFILES_DIRS = [
    BASE_DIR / "static",   # <project_root>/static
]

# مسیری که collectstatic آن را پر می‌کند (برای production)
STATIC_ROOT = BASE_DIR / "staticfiles"

# DEFAULT AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MEDIA FILES (برای آپلود نقشه‌های طراحی و فایل‌های فنی)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AUTH REDIRECTS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
