# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-textile-erp-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '*').split(',') if host.strip()]

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
]

# SESSION & CSRF COOKIES
if 'ENABLE_SECURE_COOKIES' in os.environ:
    ENABLE_SECURE_COOKIES = os.environ.get('ENABLE_SECURE_COOKIES', '').lower() in ('true', '1')
else:
    ENABLE_SECURE_COOKIES = 'APPLET_ID' in os.environ or 'CLOUD_RUN_TIMEOUT_SECONDS' in os.environ or 'RUN_APP' in os.environ

if ENABLE_SECURE_COOKIES:
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
else:
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://*.googleusercontent.com',
    'https://*.aistudio.google',
    'https://*.studio',
    'http://localhost:*',
    'http://127.0.0.1:*',
]

# Allow dynamic local network origins for CSRF
EXTRA_CSRF = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if EXTRA_CSRF:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in EXTRA_CSRF.split(',') if origin.strip()])

ROOT_URLCONF = 'textile_erp.urls'

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

# DATABASE CONFIGURATION
# PostgreSQL is the primary target database. Fallback to SQLite if PostgreSQL server is not running locally.
pg_db_config = {
    'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
    'NAME': os.environ.get('DB_NAME', 'textile_db'),
    'USER': os.environ.get('DB_USER', 'postgres'),
    'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
    'HOST': os.environ.get('DB_HOST', 'localhost'),
    'PORT': os.environ.get('DB_PORT', '5432'),
}

if os.environ.get('USE_SQLITE', '').lower() in ('true', '1'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=pg_db_config['NAME'],
            user=pg_db_config['USER'],
            password=pg_db_config['PASSWORD'],
            host=pg_db_config['HOST'],
            port=pg_db_config['PORT'],
            connect_timeout=2
        )
        conn.close()
        DATABASES = {'default': pg_db_config}
    except Exception:
        # Fallback to local SQLite if PostgreSQL connection fails
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
